"""Housekeeping tasks, preserved here just in case they're ever needed
again.
"""

import logging, os, re

from django.conf import settings

from .models import Attribute, Document, Image
from utils import extension

logger = logging.getLogger(__name__)

def cleanup(rootpath=settings.DOC_ROOT):
    "Delete image files to which no Image refers."
    for path in os.listdir(rootpath):
        images_path = os.path.join(rootpath, path, "images")

        if os.path.exists(images_path):
            for file_name in os.listdir(images_path):
                if file_name.startswith("thumb"):
                    continue

                file_path = os.path.join(images_path, file_name)

                if not Image.objects.filter(image=file_path).exists():
                    logger.info("Removing unused image file: %s", file_path)
                    os.unlink(file_path)

def remove_duplicate_attributes():
    ids = set()
    for a in Attribute.objects.all():
        if a.pk in ids:
            continue

        attrs = Attribute.objects.filter(name=a.name,
                                         proposal=a.proposal)\
                                 .exclude(pk=a.pk)
        ids.update([attr.pk for attr in attrs])

    Attribute.objects.filter(pk__in=ids).delete()

def rename_document(doc):
    docpath = doc.document and doc.document.path
    docdir, docname = os.path.split(docpath)
    ext = extension(docname)
    newpath = os.path.join(docdir, "download.%s" % ext)

    try:
        doc.move_file(newpath)
    except Exception as err:
        logger.error("Error while attempting rename:", err)
        return

def normalize_document_names():
    "Rename all local Documents to have names of the form download.<ext>."
    for doc in Document.objects.all():
        rename_document(doc)
