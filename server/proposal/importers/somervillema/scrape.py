"""
Importer for Somerville Reports and Decisions.
"""

import logging
import re
from itertools import takewhile

import pytz
from bs4 import BeautifulSoup

from . import helpers
from .events import DEFAULT_DESCRIPTIONS, title_for_case_number

try:
    from urllib.parse import urljoin
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib import urlopen, HTTPError, URLError



LOGGER = logging.getLogger(__name__)

URL_HOST = "https://www.somervillema.gov"
URL_BASE = (f"{URL_HOST}/departments/ospcd/"
            "planning-and-zoning/reports-and-decisions/robots")
URL_FORMAT = URL_BASE + "?page={:1}"
HEARING_HOUR = 18
HEARING_MIN = 0

# Give the attributes a custom name:
TITLES = {}


def attribute_for_title(title):
    """
    Convert the title (e.g., in a <th></th>) to its corresponding
    attribute in the output maps.
    """
    return TITLES.get(title, helpers.to_under(title))


# TODO: Return None or error if the response is not successful
def get_page(page=1, url_format=URL_FORMAT):
    "Returns the HTML content of the given Reports and Decisions page."
    url = url_format.format(page)
    with urlopen(url) as html_page:
        LOGGER.info("Fetching page %i", page)
        return html_page.read()


def detect_last_page(doc):
    """Given a BeautifulSoup document, returns the index of the last page.
    """
    anchor = doc.select_one("li.pager-last a")
    match = re.search(r"[?&]page=(\d+)", anchor["href"])

    return int(match.group(1)) if match else 0


def links_field(td, base=URL_BASE):
    links = helpers.get_links(td, base)
    return links and {"links": links}


def staff_report_field(td, base=URL_BASE):
    links = sum((a.find_all("a") for a in td.find_all("a")), [])
    return links and {"links": [helpers.link_info(a, base) for a in links]}



FIELD_PROCESSORS = {
    "reports": links_field,
    "decisions": links_field,
    "other": links_field,
    "first_hearing_date": helpers.optional(helpers.date_field_tz("US/Eastern")),
    "updated_date": helpers.datetime_field_tz("US/Eastern")
}


def add_geocode(geocoder, proposals):
    """
    Modifies each proposal in the list (in place), adding 'lat' and 'long'
    matching the proposal address.
    """
    addrs = [proposal["address"] for proposal in proposals]
    locations = geocoder.geocode(addrs, region="Somerville, MA")

    # Assumes the locations are returned in the same order
    for proposal, location in zip(proposals, locations):
        loc = location and location.get("location", None)
        if not loc:
            LOGGER.error("Skipping proposal {id}; geolocation failed."
                         .format(id=proposal["case_number"]))
            continue

        proposal["lat"] = loc["lat"]
        proposal["long"] = loc["lng"]
        proposal["score"] = location["properties"].get("score")


def parse_addresses(number, street):
    """Translates an address or range of addresses into a generator.
    """
    number_sublists = re.split(r"\s*/\s*", number)
    street_sublists = re.split(r"\s*/\s*", street)

    for number, street in zip(number_sublists, street_sublists):
        number_range_match = re.match(r"(\d+)-(\d+)", number)

        if number_range_match:
            yield (number_range_match.group(1), street)
            yield (number_range_match.group(2), street)
        else:
            number_sublist = re.split(r",? and |,? & |, ", number)
            for number in number_sublist:
                yield (number, street)


def get_address_list(number, street):
    """Translates an address or range of addresses into a list of addresses.
    """
    return ["{} {}".format(n, s) for (n, s) in parse_addresses(number, street)]


def find_cases(doc):
    """Takes a BeautifulSoup document, returns a list of maps representing the
    proposals found in the document.
    """
    table = helpers.find_table(doc)
    attributes = [attribute_for_title(t) for t in helpers.col_names(table)]

    tbody = table.find("tbody")
    trs = tbody.find_all("tr")

    cases = []

    for i, tr in enumerate(trs):
        try:
            proposal = helpers.get_row_vals(attributes, tr,
                                            processors=FIELD_PROCESSORS)
            addresses = get_address_list(proposal["number"], proposal["street"])
            proposal["address"] = addresses[0]
            proposal["all_addresses"] = addresses
            proposal["source"] = URL_BASE
            proposal["region_name"] = "Somerville, MA"

            # Event:
            events = []
            event_title = title_for_case_number(proposal["case_number"]),
            first_hearing = proposal.get("first_hearing_date")
            if first_hearing and event_title:
                first_hearing = first_hearing.replace(hour=HEARING_HOUR, minute=HEARING_MIN)
                events.append(
                    {"title": event_title,
                     "description": DEFAULT_DESCRIPTIONS.get(event_title),
                     "date": first_hearing,
                     "region_name": "Somerville, MA"})

            # For now, we assume that if there are one or more documents
            # linked in the 'decision' page, the proposal is 'complete'.
            # Note that we don't have insight into whether the proposal was
            # approved!
            proposal["complete"] = bool(proposal["decisions"])
            cases.append(proposal)
        except Exception as err:
            tr_string = " | ".join(tr.stripped_strings)
            LOGGER.error("Failed to scrape row %i: %s", i, tr_string)
            LOGGER.error(err)
            continue
    return cases


def get_proposals_for_page(page, geocoder=None):
    html = get_page(page)
    doc = BeautifulSoup(html, "html.parser")
    LOGGER.info("Scraping page {num}".format(num=page))
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
            LOGGER.warning("Failed to retrieve URL for page %d.", i, err)
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
                        date_column="updated_date",
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
    if not dt.tzinfo:
        dt = pytz.timezone("US/Eastern").localize(dt)

    def guard(case):
        return (not dt or case[date_column] > dt) and \
            (not stop_at_case or case["case_number"] != stop_at_case)

    all_cases = list(takewhile(guard, get_cases()))

    if geocoder:
        add_geocode(geocoder, all_cases)

    return all_cases


class SomervilleImporter(object):
    region_name = "Somerville, MA"
    zone = pytz.timezone("US/Eastern")

    def updated_since(self, since, geocoder=None):
        """Returns the proposals added or changed since the given datetime.
        """
        if not since.tzinfo:
            since = self.zone.localize(since)

        return get_proposals_since(since, geocoder=geocoder)
