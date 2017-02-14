from io import BytesIO
import re
from urllib import request

from PyPDF2 import PdfFileReader


town_ids_pdf = "http://www.mass.gov/anf/docs/itd/services/massgis/massachusetts-towns-ids-names.pdf"

def get_town_ids():
    with request.urlopen(town_ids_pdf) as u:
        pdf = PdfFileReader(BytesIO(u.read()))
        text = pdf.pages[0].extractText()
    matches = re.findall(r"\s*(\d+)([ A-Z]+)\s*", text)
    for (number, town) in matches:
        yield (int(number), town.strip().title())


def town_id_dict():
    return dict(get_town_ids())
