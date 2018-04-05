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
from shared import files
from utils import extension

from .models import Image


def save_from_url(doc, url, filename_base=None):
    """
    Downloads the document at `url` and saves it locally, storing the path in
    the given Document.

    :param doc: a Document model
    :param url: URL string
    :param filename_base: optional subpath specifying where to save the
    document

    Returns a tuple: (success, status_code, updated)
    """
    filename = path.basename(parse.urlsplit(url).path)

    if filename_base:
        filename = "{}.{}".format(filename_base, extension(filename))

    exists = doc.document and path.exists(doc.document.path)
    if exists:
        published = doc.published
        headers = {"If-Modified-Since": published.strftime("%a, %d %b %Y %H:%M:%S GMT")}
    else:
        headers = {}

    with requests.get(url, headers=headers, stream=True) as response:
        if response:
            if response.status_code == 304:
                return (True, response.status_code, False)

            doc.document.save(filename, File(response.raw), save=False)

            file_published = files.published_date(doc.document.path)

            if file_published:
                doc.published = file_published
            elif "Last-Modified" in response.headers:
                doc.published = dt_parse(response.headers["Last-Modified"])

            doc.save()
            return (True, response.status_code, exists)
        else:
            return (False, response.status_code, response.reason)


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


def extract_text(doc):
    # Could consider storing the full extracted text of the document in
    # the database and indexing it, rather than extracting it to a file.
    text_path = path.join(path.dirname(doc.local_path), "text.txt")

    if files.extract_text(doc.local_path, text_path):
        doc.fulltext = text_path
        doc.encoding = files.encoding(doc.local_path)
        doc.save()
        return True

    return False
