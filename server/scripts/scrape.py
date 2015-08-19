from bs4 import BeautifulSoup
from . import arcgis
from datetime import datetime
import json
import re
from urllib.request import urlopen
from urllib.error import HTTPError

LAST_PAGE = 31
URL_FORMAT = "http://www.somervillema.gov/planningandzoning/reports?order=field_rnd_submission_date_value&sort=desc&page={:1}"
TITLES = {}
DATE_FORMAT = "%b %d, %Y"

def make_url(page=1):
    "Returns a string URL for the given page."
    return URL_FORMAT.format(page)

# Utility:
def to_camel(s):
    "Converts a string s to camelCase."
    return re.sub(r"[\s\-_](\w)", lambda m: m.group(1).upper(), s.lower())

def attribute_for_title(title):
    """
    Convert the title (e.g., in a <th></th>) to its corresponding
    attribute in the output maps.
    """
    return TITLES.get(title, to_camel(title))

# TODO: Return None or error if the response is not successful
def get_page(page=1):
    "Returns the HTML content of the given Reports and Decisions page."
    f = urlopen(make_url(page))
    html = f.read()
    f.close()
    return html

def find_table(doc):
    return doc.select_one("table.views-table")

def detect_last_page(doc):
    anchor = doc.select_one("li.pager-last a")
    m = re.search(r"[?&]page=(\d+)", anchor["href"])

    if m:
        return int(m.group(1))

    return 0

## Field helpers:
def link_info(a):
    return {
        "title": a.get_text().strip(),
        "url": a["href"]
    }

def get_date(d):
    return datetime.strptime(d, '%b %d, %Y')

def get_links(elt):
    "Return information about the <a> element descendants of elt."
    return [link_info(a) for a in elt.find_all("a") if a["href"]]

def dates_field(td):
    return get_date(default_field(td))

def links_field(td):
    return {"links": get_links(td)}

def default_field(td):
    return td.get_text().strip()

field_processors = {
    "reports": links_field,
    "decisions": links_field,
    "other": links_field,
    "submissionDate": dates_field
}

def col_names(table):
    tr = table.select_one("thead > tr")
    return [th.get_text().strip() for th in tr.find_all("th")]

def get_td_val(td, attr=None):
    processor = field_processors.get(attr, default_field)
    return processor(td)

def get_row_vals(attrs, tr):
    return {attr: get_td_val(td, attr) for attr, td in zip(attrs, tr.find_all("td"))}

def add_geocode(permits):
    """
    Modifies each permit in the list (in place), adding 'lat' and 'long'
    matching the permit address.
    """
    addrs = ["{0[number]} {0[street]}".format(permit) for permit in permits]
    response = arcgis.geocode(addrs)
    locations = response["locations"]

    # Assumes the locations are returned in the same order
    for permit, location in zip(permits, locations):
        loc = location["location"]
        permit["lat"] = loc["y"]
        permit["long"] = loc["x"]
        permit["score"] = location["score"]

def find_cases(doc):
    table = find_table(doc)
    titles = col_names(table)
    attributes = [attribute_for_title(t) for t in titles]

    tbody = table.find("tbody")
    trs = tbody.find_all("tr")
    return [get_row_vals(attributes, tr) for tr in trs]

def index_by(l, keyfn):
    if isinstance(keyfn, str):
        s = keyfn
        keyfn = lambda o: o[s]

    return {keyfn(o): o for o in l}

def get_proposals_since(dt, date_column="submissionDate",
                        geocode=True):
    """
    Continually scrape the proposals until the submission date is
    less than or equal to the given date.

    Returns an array of dicts representing scraped cases.
    """
    all_cases = []
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

        if not html:
            break

        doc = BeautifulSoup(html, "html.parser")
        cases = find_cases(doc)
        all_cases += [case for case in cases if case[date_column] > dt]

        if cases[-1][date_column] <= dt:
            break

        if last_page is None:
            last_page = detect_last_page(doc)

        i += 1

        if i > last_page:
            break

    if geocode:
        add_geocode(all_cases)

    return all_cases

# Deprecate the old name:
get_permits_since = get_proposals_since
get_permits = get_proposals
