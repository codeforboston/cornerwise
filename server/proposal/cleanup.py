"""Housekeeping tasks, preserved here just in case they're ever needed
again.
"""

import logging
import os

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


def make_file_mover(attr):
    """Returns a function that takes an object and a new name and renames
    the file associated with that object's `attr` file field.

    :param attr: The name of the FileField attribute on the target
    object

    :returns: A function that can be bound as a method of an object with
    the named file field.

    """
    def move_file(self, new_path):
        file_field = getattr(self, attr)
        current_path = file_field and file_field.path

        if not current_path:
            raise IOError("")

        if os.path.basename(new_path) == new_path:
            doc_dir, _ = os.path.split(current_path)
            new_path = os.path.join(doc_dir, new_path)

        if new_path != current_path:
            os.rename(current_path, new_path)

            try:
                setattr(self, attr, new_path)
                self.save()
            except Exception as err:
                os.rename(new_path, self.local_file)

                raise err

        return new_path

    return move_file


do_rename = make_file_mover("document")


def rename_document(doc):
    docpath = doc.document and doc.document.path
    if not docpath:
        logger.error("Document %s has no local file" % doc.pk)
        return

    docdir, docname = os.path.split(docpath)
    ext = extension(docname)
    new_path = os.path.join(docdir, "download.%s" % ext)

    try:
        do_rename(doc, new_path)
    except Exception as err:
        logger.error("Error while attempting rename:", err)
        return


def normalize_document_names():
    "Rename all local Documents to have names of the form download.<ext>."
    for doc in Document.objects.all():
        rename_document(doc)
