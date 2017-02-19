"""
Helper functions for working with Documents.
"""

from django.core.files import File

from dateutil.parser import parse as dt_parse
from os import path
from dateutil.parser import parse
import shutil
import subprocess
from urllib import parse, request

from scripts import pdf
from shared import files_metadata
from utils import extension

from .models import Image


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
    for i, (image_data, ext, w, h) in enumerate(image_gen):
        image = Image(proposal=doc.proposal, document=doc)
        image.width = w
        image.height = h
        image.image.save("image-{:0>3}.{}".format(i, ext), image_data)
        images.append(image)

    return images


def generate_thumbnail(doc):
    "Generate a Document thumbnail."
    if not doc.document:
        task_logger.error("Document has not been copied to the local filesystem")
        return

    path = doc.document.path

    # TODO: Dispatch on extension. Handle other common file types
    if extension(path) != "pdf":
        return

    out_prefix = path.join(path.dirname(path), "thumbnail")

    proc = subprocess.Popen(
        [
            "pdftoppm", "-jpeg", "-singlefile", "-scale-to", "200", path,
            out_prefix
        ],
        stderr=subprocess.PIPE)
    _, err = proc.communicate()

    if proc.returncode:
        raise Exception("Failed for document %s" % doc.pk, err)

    thumb_path = out_prefix + path.extsep + "jpg"
    with open(thumb_path, "rb") as thumb_file:
        doc.thumbnail.save("thumbnail.jpg", File(thumb_file))

    return thumb_path
