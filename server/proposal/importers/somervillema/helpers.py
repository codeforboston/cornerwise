from datetime import datetime
import re
import pytz
from functools import partial


def to_camel(s):
    "Converts a string s to camelCase."
    return re.sub(r"[\s\-_](\w)", lambda m: m.group(1).upper(), s.lower())


def link_info(a):
    return {
        "title": a.get_text().strip(),
        "url": a["href"]
    }


def get_date(d):
    return datetime.strptime(d, '%b %d, %Y')


def get_datetime(datestring, tzinfo=None):
    dt = datetime.strptime(datestring,
                           "%m/%d/%Y - %I:%M%p")
    if tzinfo:
        return tzinfo.localize(dt)

    return dt


def get_links(elt):
    "Return information about the <a> element descendants of elt."
    return [link_info(a) for a in elt.find_all("a") if a["href"]]


# Field processors:
def dates_field(td):
    return get_date(default_field(td))


def datetime_field(td, tzinfo=None):
    return get_datetime(default_field(td), tzinfo)


def datetime_field_tz(tz):
    if isinstance(tz, str):
        tz = pytz.timezone(tz)
    return partial(datetime_field, tzinfo=tz)


def links_field(td):
    return {"links": get_links(td)}


def default_field(td):
    return td.get_text().strip()


def get_td_value(td, attr=None, processors={}):
    processor = processors.get(attr, default_field)
    return processor(td)


def get_row_vals(attrs, tr, processors={}):
    return {attr: get_td_value(td, attr, processors=processors) \
            for attr, td in zip(attrs, tr.find_all("td"))}


def col_names(table):
    tr = table.select_one("thead > tr")
    return [th.get_text().strip() for th in tr.find_all("th")]


def find_table(doc):
    return doc.select_one("table.views-table")


def get_data(doc, get_attribute=to_camel, processors={}):
    table = find_table(doc)
    titles = col_names(table)
    attributes = [get_attribute(t) for t in titles]

    trs = table.find("tbody").find_all("tr")
    for i, tr in enumerate(trs):
        yield get_row_vals(attributes, tr, processors)
