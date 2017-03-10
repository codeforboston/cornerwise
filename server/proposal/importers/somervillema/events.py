from datetime import datetime
from io import BytesIO
import itertools
import pytz
import re
from urllib.request import urlopen

from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader
from PyPDF2.utils import PdfReadError

EVENTS_URL = "http://archive.somervillema.gov/PubMtgs.cfm"

# This is hard-coded, because it's difficult to consistently extract from the
# PDF.
DEFAULT_LOCATION = ("Aldermanic Chambers, Somerville City Hall, "
                    "Second Floor, 93 Highland Ave")
DEFAULT_DESCRIPTIONS = {"Zoning Board of Appeals": ("The ZBA is the Special Permit Granting Authority for variances; appeals of decisions; Comprehensive Permit Petitions; and some Special Permit applications"),

                        "Planning Board": ("The Planning Board is the Special Permit Granting Authority for special districts and makes recommendations to the Board of Aldermen on zoning amendments.")}

DATE_FORMAT = "%b %d, %Y"
POSTING_FORMAT = "%m/%d/%Y - %I:%M%p"

# All the dates and times on the Somerville site are in this timezone.
# Mysterious!
TZ = pytz.timezone("US/Eastern")


def title_for_case_number(case_number):
    if case_number.startswith("PB"):
        return "Planning Board"

    if case_number.startswith("ZBA"):
        return "Zoning Board of Appeals"


def get_page(url):
    with urlopen(url) as u:
        return BeautifulSoup(u.read(), "html.parser")


def get_pdf(url):
    with urlopen(url) as u:
        contents = u.read()
        pdf_buffer = BytesIO(contents)

    return PdfFileReader(pdf_buffer)


def pdf_lines(pdf):
    for page in pdf.pages:
        for line in page.extractText().splitlines():
            yield line


def to_cases(lines):
    current_case = None
    for line in lines:
        m = re.search(r"\(\s*Case #((ZBA|PB) \d+\-\d+)", line)
        if m:
            if current_case:
                yield current_case
            current_case = {"number": m.group(1), "lines": []}
        elif current_case:
            # TODO: Extract more structured data from these lines!
            current_case["lines"].append(line)

    if current_case:
        yield current_case


def html_contents(title, tag):
    a = tag.find("a")

    if a:
        return {"title": a.get_text().strip(), "url": a.attrs.get("href")}

    content = tag.get_text().strip()

    if title == "Agenda Posting Date":
        return datetime.strptime(content, POSTING_FORMAT)

    if title == "Date":
        return datetime.strptime(content, DATE_FORMAT)

    return content


def to_row(titles, tr):
    return {
        k: html_contents(k, td)
        for k, td in zip(titles, tr.find_all("td"))
    }


def data_rows(doc):
    table = doc.select_one("table.views-table")
    thead = table.find("thead")
    titles = [th.get_text().strip() for th in thead.find_all("th")]

    tbody = table.find("tbody")
    trs = tbody.find_all("tr")
    return [to_row(titles, tr) for tr in trs]


def page_events(url, filt=lambda _: True):
    page = get_page(url)
    for row in filter(filt, data_rows(page)):
        agenda_url = row["Agenda"]["url"]

        try:
            agenda_lines = pdf_lines(get_pdf(agenda_url))
        except PdfReadError:
            continue

        case_numbers = [case["number"] for case in to_cases(agenda_lines)]

        # Record as local datetime!
        date = TZ.localize(row["Date"].replace(hour=18, minute=0))

        # Record this in UTC!
        posted = TZ.localize(row["Agenda Posting Date"]).astimezone(pytz.UTC)
        title = row["Meeting"]["title"]

        yield {
            "date": date,
            "posted": posted,
            "title": title,
            "description": DEFAULT_DESCRIPTIONS.get(title),
            "agenda_url": agenda_url,
            "cases": case_numbers,
            "location": DEFAULT_LOCATION,
            "region_name": "Somerville, MA"
        }


def get_events(since=None):
    events = page_events(EVENTS_URL)

    if since:
        if not since.tzinfo:
            since = TZ.localize(since)

        def is_recent(row):
            return row["posted"] > since

        events = itertools.takewhile(is_recent, events)

    return (e for e in events if e["title"] in {"Planning Board",
                                                "Zoning Board of Appeals"})


class EventsImporter(object):
    region_name = "Somerville, MA"

    def updated_since(self, dt):
        return get_events(dt)

