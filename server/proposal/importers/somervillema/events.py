from datetime import datetime
from io import BytesIO
import itertools
import pytz
import re
from urllib.request import urlopen

from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader

URL_BASE = "http://www.somervillema.gov/government/public-minutes"

ZBA_URL = "http://www.somervillema.gov/government/public-minutes?field_event_org_unit_nid=216"
PB_URL = "http://www.somervillema.gov/government/public-minutes?field_event_org_unit_nid=206"

# This is hard-coded, because it's difficult to consistently extract from the
# PDF.
DEFAULT_LOCATION = ("Aldermanic Chambers, Somerville City Hall, "
                    "Second Floor, 93 Highland Ave")

DATE_FORMAT = "%b %d, %Y"
POSTING_FORMAT = "%m/%d/%Y - %I:%M%p"

# All the dates and times on the Somerville site are in this timezone.
# Mysterious!
TIMEZONE = pytz.timezone("US/Eastern")


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
        m = re.search(r"\(\s*Case #((ZBA|PB) \d+\-\d+)\s*\)", line)
        if m:
            if current_case:
                yield current_case
            current_case = {"number": m.group(1), "lines": []}
        elif current_case:
            current_case["lines"].append(line)

    if current_case:
        yield current_case


def to_properties(lines):
    pass


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

        agenda_lines = pdf_lines(get_pdf(agenda_url))
        case_numbers = [case["number"] for case in to_cases(agenda_lines)]

        # Record as local datetime!
        date = row["Date"]
        date.replace(hour=6, minute=0)
        date = TIMEZONE.localize(date)

        # Record this in UTC!
        posted = TIMEZONE.localize(row["Agenda Posting Date"]).astimezone(pytz.UTC)

        yield {
            "date": date,
            "posted": posted,
            "title": row["Meeting"]["title"],
            "agenda_url": agenda_url,
            "cases": case_numbers,
            "location": DEFAULT_LOCATION,
            "region_name": "Somerville, MA"
        }


def zba_events():
    return page_events(ZBA_URL)


def pb_events():
    def filt(row):
        return row["Meeting"]["title"] == "Planning Board"

    return page_events(PB_URL, filt)

def get_events(since=None):
    zba = zba_events()
    pb = pb_events()

    if since:
        if not since.tzinfo:
            since = TIMEZONE.localize(since)

        def is_recent(row):
            return row["posted"] > since

        zba = itertools.takewhile(is_recent, zba)
        pb = itertools.takewhile(is_recent, pb)

    return itertools.chain(zba, pb)


class EventsImporter(object):
    region_name = "Somerville, MA"

    def updated_since(self, dt):
        return get_events()

