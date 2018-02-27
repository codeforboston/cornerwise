"""
Helper functions for working with Documents.
"""

from django.core.files import File

from dateutil.parser import parse as dt_parse
from os import path
import subprocess
from urllib import parse

import requests

from scripts import pdf
from shared import files_metadata
from utils import extension

from .models import Image


def last_modified(url):
    headers = requests.head(url).headers

    if "Last-Modified" in headers:
        return dt_parse(headers["Last-Modified"])

    return None


def save_from_url(doc, url, filename_base=None):
    filename = path.basename(parse.urlsplit(url).path)

    if filename_base:
        filename = "{}.{}".format(filename_base, extension(filename))

    with requests.get(url, stream=True) as response:
        doc.document.save(filename, File(response.raw), save=False)

        file_published = files_metadata.published_date(path)

        if file_published:
            doc.published = file_published
        elif "Last-Modified" in response.headers:
            doc.published = dt_parse(response.headers["Last-Modified"])

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
        image.save()
        images.append(image)

    return images


def generate_thumbnail(doc):
    "Generate a Document thumbnail."
    if not doc.document:
        raise FileNotFoundError(
            "Document has not been copied to the local filesystem")

    doc_path = doc.document.path

    # TODO: Dispatch on extension. Handle other common file types
    if extension(doc_path) != "pdf":
        return

    out_prefix = path.join(path.dirname(doc_path), "thumbnail")

    proc = subprocess.Popen(
        [
            "pdftoppm", "-jpeg", "-singlefile", "-scale-to", "200", doc_path,
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
