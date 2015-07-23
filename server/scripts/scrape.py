from bs4 import BeautifulSoup
import re
import urllib2

LAST_PAGE = 31
URL_FORMAT = "http://www.somervillema.gov/planningandzoning/reports?page={:1}"
TITLES = {}

def to_camel(s):
    "Converts a string s to camelCase."
    return re.sub(r"[\s\-_](\w)", lambda m: m.group(1).upper(), s.lower())

def attribute_for_title(title):
    return TITLES.get(title, to_camel(title))

def make_url(page=1):
    return URL_FORMAT.format(page)

def get_page(page=1):
    f = urllib2.urlopen(make_url(page))
    html = f.read()
    f.close()
    return html

def find_table(doc):
    return doc.select_one("table.views-table")

def col_names(table):
    tr = table.select_one("thead > tr")
    return [th.get_text().strip() for th in tr.find_all("th")]

def get_td_val(td, attr=None):
    return td.get_text().strip()

def get_row_vals(attrs, tr):
    return {attr: get_td_val(td, attr) for attr, td in zip(attrs, tr.find_all("td"))}

def find_cases(doc):
    table = find_table(doc)
    titles = col_names(table)
    attributes = [attribute_for_title(t) for t in titles]

    tbody = table.find("tbody")
    trs = tbody.find_all("tr")
    return [get_row_vals(attributes, tr) for tr in trs]

def main(pages):
    # Indexed by case number:
    cases = {}
    for i in pages:
        doc = BeautifulSoup(get_page(i))
        case_list = find_cases(doc)
        for case in case_list:
            cases[case["caseNumber"]]

    return cases
    #BeautifulSoup()

if __name__ == "__main__":
    print(main(range(1, LAST_PAGE+1)))
