from bs4 import BeautifulSoup
from itertools import takewhile
import logging
import pytz
import re
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

from . import helpers

logger = logging.getLogger(__name__)

URL_BASE = "http://www.somervillema.gov/departments/planning-board/reports-and-decisions/robots"
URL_FORMAT = URL_BASE + "?page={:1}"

# Give the attributes a custom name:
TITLES = {}


def attribute_for_title(title):
    """
    Convert the title (e.g., in a <th></th>) to its corresponding
    attribute in the output maps.
    """
    return TITLES.get(title, helpers.to_camel(title))


# TODO: Return None or error if the response is not successful
def get_page(page=1, url_format=URL_FORMAT):
    "Returns the HTML content of the given Reports and Decisions page."
    url = url_format.format(page)
    f = urlopen(url)
    logger.info("Fetching page {}".format(page))
    html = f.read()
    f.close()
    return html


def detect_last_page(doc):
    anchor = doc.select_one("li.pager-last a")
    m = re.search(r"[?&]page=(\d+)", anchor["href"])

    if m:
        return int(m.group(1))

    return 0


## Field helpers:

def get_links(elt):
    "Return information about the <a> element descendants of elt."
    return [helpers.link_info(a) for a in elt.find_all("a") if a["href"]]


def default_field(td):
    return td.get_text().strip()

field_processors = {
    "reports": helpers.links_field,
    "decisions": helpers.links_field,
    "other": helpers.links_field,
    "firstHearingDate": helpers.dates_field,
    "updatedDate": helpers.datetime_field_tz("US/Eastern")
}


def get_td_val(td, attr=None):
    processor = field_processors.get(attr, default_field)
    return processor(td)


def add_geocode(geocoder, proposals):
    """
    Modifies each proposal in the list (in place), adding 'lat' and 'long'
    matching the proposal address.
    """
    addrs = ["{0[number]} {0[street]}".format(proposal) for proposal in
             proposals]
    locations = geocoder.geocode(addrs)

    # Assumes the locations are returned in the same order
    for proposal, location in zip(proposals, locations):
        loc = location and location.get("location")
        if not loc:
            logger.error("Skipping proposal {id}; geolocation failed."
                         .format(id=proposal["caseNumber"]))
            continue

        proposal["lat"] = loc["lat"]
        proposal["long"] = loc["lng"]
        proposal["score"] = location["properties"].get("score")


def find_cases(doc):
    table = helpers.find_table(doc)
    titles = helpers.col_names(table)
    attributes = [attribute_for_title(t) for t in titles]

    tbody = table.find("tbody")
    trs = tbody.find_all("tr")

    cases = []

    # This is ugly, but there's some baaad data out there:
    for i, tr in enumerate(trs):
        try:
            proposal = helpers.get_row_vals(attributes, tr,
                                            processors=field_processors)
            proposal["address"] = "{} {}".format(proposal["number"],
                                                 proposal["street"])
            proposal["source"] = URL_BASE
            proposal["region_name"] = "Somerville, MA"

            # For now, we assume that if there are one or more documents
            # linked in the 'decision' page, the proposal is 'complete'.
            # Note that we don't have insight into whether the proposal was
            # approved!
            proposal["complete"] = bool(proposal["decisions"])
            cases.append(proposal)
        except Exception as err:
            logger.error("Failed to scrape row", i, tr)
            logger.error(err)
            continue
    return cases


def get_proposals_for_page(page, geocoder=None):
    html = get_page(page)
    doc = BeautifulSoup(html, "html.parser")
    logger.info("Scraping page {num}".format(num=page))
    cases = find_cases(doc)

    if geocoder:
        add_geocode(geocoder, cases)

    return cases


def get_pages():
    """Returns a generator that retrieves Reports and Decisions pages and
    parses them as HTML.

    """
    i = 0
    last_page = None

    while True:
        try:
            # There's currently a bug in the Reports and Decisions page
            # that causes nonexistent pages to load page 1. They should
            # return a 404 error instead!
            html = get_page(i)
        except HTTPError as err:
            break

        except URLError as err:
            logger.warn("Failed to retrieve URL for page %d.", i,
                        err)
            break

        doc = BeautifulSoup(html, "html.parser")
        if last_page is None:
            last_page = detect_last_page(doc)

        yield doc

        i += 1

        if i > last_page:
            break


def get_cases(gen=None):
    "Returns a generator that produces cases."
    if not gen:
        gen = get_pages()

    for doc in gen:
        for case in find_cases(doc):
            yield case


def get_proposals_since(dt=None,
                        stop_at_case=None,
                        date_column="updatedDate",
                        geocoder=None):
    """Page through the Reports and Decisions page, scraping the proposals
    until the submission date is less than or equal to the given date.

    :param dt: If provided, stop scraping when the `date_column` is less
    than or equal to this datetime.

    :param stop_at_case: If provided, stop scraping when a case number
    matches this string

    :param date_column: Customize the name of the date column

    :geocoder: An object with a geocode() method that accepts a list
    of string addresses.

    :returns: A list of dicts representing scraped cases.

    """
    def guard(case):
        return (not dt or case[date_column] > dt) and \
            (not stop_at_case or case["caseNumber"] != stop_at_case)

    all_cases = list(takewhile(guard, get_cases()))

    if geocoder:
        add_geocode(geocoder, all_cases)

    return all_cases


class Importer(object):
    region_name = "Somerville, MA"
    tz = pytz.timezone("US/Eastern")

    def updated_since(self, dt, geocoder=None):
        if not dt.tzinfo:
            dt = self.tz.localize(dt)
        
        return get_proposals_since(dt, geocoder=geocoder)
