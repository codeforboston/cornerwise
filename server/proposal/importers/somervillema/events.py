from bs4 import BeautifulSoup
from urllib.request import urlopen
from . import helpers

URL_BASE = "http://www.somervillema.gov/government/public-minutes"


def get_page():
    url = URL_BASE

    with urlopen(url) as f:
        return BeautifulSoup(f.read(), "html.parser")


processors = {
    "meeting": helpers.links_field,
    "date": helpers.dates_field,
    "agenda": helpers.links_field,
    "agendaPostingDate": helpers.datetime_field
}


def get_events():
    return helpers.get_data(get_page(),
                            processors=processors)
