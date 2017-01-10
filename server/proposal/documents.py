"""
Helper functions for working with Documents.
"""

from django.core.files import File

from dateutil.parser import parse as dt_parse
from os import path
from dateutil.parser import parse
import shutil
from urllib import parse, request

from shared import files_metadata
from utils import extension


def last_modified(url):
    req = request.Request(url=url, method="HEAD")
    with request.urlopen(req) as resp:
        if "Last-Modified" in resp.headers:
            return parse(resp.headers["Last-Modified"])

    return None


def doc_info(doc):
    enc = doc.encoding
    if doc.fulltext and doc.fulltext.path:
        lines = (line.decode(enc) for line in doc.fulltext)
    else:
        lines = []

    return {"field": doc.field, "title": doc.title, "lines": lines}


def save_from_url(doc, url, filename_base=None):
    filename = path.basename(parse.urlsplit(url).path)

    if filename_base:
        filename = "{}.{}".format(filename_base, extension(filename))

    with request.urlopen(url) as resp:
        doc.document.save(filename, File(resp), save=False)

        file_published = files_metadata.published_date(path)

        if file_published:
            doc.published = file_published
        elif "Last-Modified" in resp.headers:
            doc.published = dt_parse(resp.headers["Last-Modified"])

        doc.save()

    return doc


def save_images(doc):
    if not doc.document:
        raise Exception("Document has not been copied to the local filesystem.")
        return []

    path = doc.document.path
    image_gen = pdf.extract_images(path)

    images = []
    # Do stuff with the images in the directory
    for i, (image_data, ext) in enumerate(image_gen):
        image = Image(proposal=doc.proposal, document=doc)
        image.image.save("image-{:0>3}.{}".format(i, ext), image_data)
        images.append(image)

    return images
