"""Celery tasks for import and processing of Proposals, Events, and Projects
and their related models (Documents, Images).
"""
from datetime import datetime, timedelta
import os
import pytz
import re
import subprocess

import celery
from celery.utils.log import get_task_logger

from django.conf import settings
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models import F, QuerySet
from django.db.models.signals import post_save
from django.db.utils import DataError, IntegrityError

from cornerwise.adapt import adapt
from utils import add_locations
from scripts import foursquare, images, street_view, vision
from shared.geocoder import Geocoder
from .models import Proposal, Document, Event, Image, Importer
from . import extract, documents as doc_utils


task_logger = get_task_logger(__name__)
shared_task = celery.shared_task


@shared_task
@adapt
def fetch_document(doc: Document):
    """Copy the given document (proposal.models.Document) to a local
    directory.
    """
    url = doc.url

    if doc.document and os.path.exists(doc.document.path):
        # Has the document been updated?
        updated = doc_utils.last_modified(doc.url)
        # No?  Then we're good.
        if not updated or updated <= doc.published:
            return doc.pk

    task_logger.info("Fetching Document #%i", doc.pk)
    doc_utils.save_from_url(doc, url, "download")
    task_logger.info("Copied Document #%i to %s", doc.pk, doc.document.path)

    return doc.pk


@shared_task
@adapt
def extract_text(doc: Document, encoding="ISO-8859-9"):
    """If a document is a PDF that has been copied to the filesystem, extract its
    text contents to a file and save the path of the text document.

    :param doc: proposal.models.Document object

    :returns: The same document

    """
    path = doc.local_path
    # Could consider storing the full extracted text of the document in
    # the database and indexing it, rather than extracting it to a file.
    text_path = os.path.join(os.path.dirname(path), "text.txt")

    # TODO: It may be practical to sniff pdfinfo, determine the PDF
    # producer used, and make a best guess at encoding based on that
    # information. We should be able to get away with using ISO-8859-9
    # for now.
    status = subprocess.call(["pdftotext", "-enc", encoding, path, text_path])

    if status:
        task_logger.error("Failed to extract text from %s", path)
    else:
        task_logger.info("Extracted text from Document #%i to %s.", doc.pk,
                         doc.fulltext)
        doc.fulltext = text_path
        doc.encoding = encoding
        doc.save()

        return doc.pk


@shared_task
@adapt
def extract_images(doc: Document):
    """If the given document (proposal.models.Document) has been copied to
    the local filesystem, extract its images to a subdirectory of the
    document's directory (docs/<doc id>/images).

    :param doc: id of a proposal.models.Document object with a corresponding
    PDF file that has been copied to the local filesystem

    :returns: A list of proposal.models.Image objects

    """
    try:
        task_logger.info("Extracting images from Document #%s", doc.pk)
        images = doc_utils.save_images(doc)
        task_logger.info("Extracted %i image(s) from %s.", len(images), doc.title)

        return [image.pk for image in images]
    except Exception as exc:
        task_logger.error(exc)

        return []


@shared_task
@adapt
def add_street_view(proposal: Proposal):
    api_key = getattr(settings, "GOOGLE_API_KEY")
    secret = getattr(settings, "GOOGLE_STREET_VIEW_SECRET")

    if api_key:
        location = "{0.address}, {0.region_name}".format(proposal)
        url = street_view.street_view_url(location, api_key, secret=secret)
        try:
            # Check that there is not already a Street View image associated
            # with this proposal:
            if not proposal.images\
                           .filter(source="google_street_view")\
                           .exists():
                image = proposal.images.create(
                    url=url,
                    skip_cache=True,
                    source="google_street_view",
                    height=640,
                    width=640,
                    priority=1)
                return image
        except IntegrityError:
            task_logger.warning("Image with that URL already exists: %s", url)
        except DataError:
            task_logger.error(
                "Image could not be saved.  Was the URL too long? %s", url)

    else:
        task_logger.warn("Add a local_settings file with your Google API key "
                         + "to add Street View images.")


@shared_task
@adapt
def add_venue_info(proposal: Proposal):
    client_id = getattr(settings, "FOURSQUARE_CLIENT", None)
    client_secret = getattr(settings, "FOURSQUARE_SECRET")

    if not (client_id and client_secret):
        return

    lng, lat = proposal.location.coords
    params = {"lat": lat, "lng": lng, "address": proposal.address}
    venue = foursquare.find_venue(params, client_id, client_secret)

    if venue:
        task_logger.info("Found matching venue for proposal #{}: {}"\
                         .format(proposal.id, venue["id"]))
        proposal.attributes.create(
            name="foursquare_id", text_value=venue["id"])
        proposal.attributes.create(
            name="foursquare_name", text_value=venue["name"])
        if venue["url"]:
            proposal.attributes.create(
                name="foursquare_url", text_value=venue["url"])

    return proposal.id


@shared_task
@adapt
def add_parcel(proposal: Proposal):
    from parcel.models import Parcel

    parcels = Parcel.objects.containing(proposal.location).exclude(poly_type="ROW")
    if parcels:
        proposal.parcel = parcels[0]
        proposal.save()

        return proposal.id


@shared_task
@adapt
def generate_doc_thumbnail(doc: Document):
    "Generate a Document thumbnail."
    if not doc.document:
        task_logger.error(
            "Document has not been copied to the local filesystem")
        return

    return doc_utils.generate_thumbnail(doc)


@shared_task
def generate_thumbnail(image_id, replace=False):
    """Generate an image thumbnail.

    :param image: A proposal.model.Image object with a corresponding
    image file on the local filesystem.

    :returns: Thumbnail path"""

    image = Image.objects.get(pk=image_id)
    thumbnail_path = image.thumbnail and image.thumbnail.name
    if thumbnail_path and os.path.exists(thumbnail_path):
        task_logger.info("Thumbnail already exists (%s)", image.thumbnail.name)
    else:
        if not image.image:
            task_logger.info("No local image for Image #%s", image.pk)
            return

        try:
            thumbnail_path = images.make_thumbnail(
                image.image.path, fit=settings.THUMBNAIL_DIM)
        except Exception as err:
            task_logger.error(err)
            return

        task_logger.info("Generate thumbnail for Image #%i: %s", image.pk,
                         thumbnail_path)
        image.thumbnail = thumbnail_path
        image.save()

    return thumbnail_path


@shared_task
@adapt
def add_doc_attributes(doc: Document):
    props = extract.get_properties(doc)

    doc.proposal.update_from_dict(props)

    return doc.pk


@shared_task
def generate_thumbnails(image_ids):
    for image_id in image_ids:
        try:
            generate_thumbnail(image_id)
        except Image.DoesNotExist:
            task_logger.info(
                f"Image #{image_id} was deleted before thumbnail generation"
            )
            continue


@shared_task
@adapt
def save_image_text(doc: Document, image_ids):
    if not len(image_ids):
        return

    all_text = [t for t in [cache.get(f"image:{image_id}:text")
                            for image_id in image_ids] if t]

    if all_text:
        text_path = os.path.join(os.path.dirname(doc.local_path), "text.txt")
        with open(text_path, "a") as fulltext:
            for text in all_text:
                fulltext.write(text)
                fulltext.write("\n")
        doc.encoding = "utf-8"
        doc.fulltext = text_path
        doc.save()


@shared_task
@adapt
def post_process_images(doc: Document, image_ids):
    task_logger.info(
        f"Post processing image ids {image_ids} for doc {doc.pk}")
    for image_id in image_ids:
        cloud_vision_process(image_id)
    generate_thumbnails(image_ids)
    save_image_text(doc.id, image_ids)

    return image_ids


@shared_task
@adapt
def process_document_sync(doc: Document):
    fetch_document(doc)

    extract_text(doc)
    add_doc_attributes(doc)

    image_ids = extract_images(doc)
    post_process_images(doc, image_ids)

    generate_doc_thumbnail(doc)


def process_document(doc):
    """
    Run all tasks on a Document.
    """
    (fetch_document.s(doc.id) |
     celery.group(extract_images.s() | post_process_images.s(),
                  generate_doc_thumbnail.s(),
                  extract_text.s() | add_doc_attributes.s()))()


def process_proposal(proposal):
    "Perform additional processing on proposals."
    # Create a Google Street View image for each proposal:
    add_street_view.delay(proposal.id)
    #add_venue_info.delay(proposal.id)

    add_parcel.delay(proposal.id)

    return proposal.id


def stringify_address_dict(address):
    return f"{address.street_address}, {address.city}, {address.state}"


def create_proposals(dicts):
    """Helper function to create new Proposal objects.
    """

    for case_dict in dicts:
        try:
            (_, p) = Proposal.create_or_update_from_dict(case_dict)
            p.importer = case_dict.get("importer")
            p.save() # Needed?
            yield p
        except Exception as exc:
            import pprint
            from io import StringIO
            buff = StringIO()
            pprint.pprint(case_dict, buff)
            print(f"Could not create create proposal from: {buff.getvalue()}")
            print(exc)
            task_logger.error("Could not create proposal from dictionary: %s",
                              case_dict)
            task_logger.error("%s", exc)


def create_events(dicts):
    for event_dict in dicts:
        yield Event.objects.make_event(event_dict)


@adapt
def fetch_proposals(since: datetime=None,
                    importers: QuerySet=None):
    """Task runs each of the importers given.

    """
    now = pytz.utc.localize(datetime.utcnow().replace(hour=0, minute=8,
                                                      second=0, microsecond=0))

    latest_proposal = Proposal.objects.latest()
    if latest_proposal:
        default_since = latest_proposal.updated
    else:
        # If there is no record of a previous run, fetch
        # proposals posted since the previous Monday.
        default_since = now - timedelta(days=7 + now.weekday())

    if importers is None:
        importers = Importer.objects.all()

    all_found = {"cases": [], "events": [], "projects": []}
    for importer in importers:
        importer_since = since
        if not since:
            if importer.last_run:
                importer_since = importer.last_run
            else:
                importer_since = default_since

        importer_since = \
            importer.tz.normalize(importer_since) if importer_since.tzinfo \
            else importer_since

        try:
            found = importer.updated_since(importer_since)
            importer.validate(found)
        except Exception as err:
            task_logger.warning("Importer %s failed schema validation!\n%s",
                                importer.name, err)
            continue

        found_description = ", ".join(f"{len(v)} {k}" for k, v in found.items())
        task_logger.info(f"Fetched: {found_description} w/{importer}")

        for k in found:
            for item in found[k]:
                if "region_name" not in item:
                    item["region_name"] = importer.region_name
                item["importer"] = importer
                all_found[k].append(item)

        importer.last_run = now
        importer.save()

    add_locations(all_found["cases"], Geocoder)

    #     add_locations(all_found["projects"],
    #                   lambda prj: stringify_address_dict(prj["address"]))

    proposal_ids = [p.id for p in create_proposals(all_found["cases"])]
    return proposal_ids


@shared_task
def pull_updates(since: datetime=None, importers_filter: str=None):
    "Run all registered proposal importers."
    filters = {}
    if importers_filter:
        filters["region_name__icontains"] = importers_filter

    return fetch_proposals(since,
                           importers=Importer.objects.filter(**filters))


# Image tasks
@shared_task
def cloud_vision_process(image_id):
    """
    Send the image to the Cloud Vision API. If the image is recognized as a
    logo, delete it.
    """
    processed_key = f"image:{image_id}:checked"
    image = Image.objects.annotate(region_name=F("proposal__region_name"))\
                         .get(pk=image_id)
    if cache.get(processed_key):
        return

    city_name = re.split(r"\s*,\s*", image.region_name, 1)[0]
    processed = vision.process_image(image.image and image.image.path, image.url)
    logo = processed["logo"]
    if logo:
        if city_name in logo["description"]:
            image.delete()
            task_logger.info("Logo detected: image #%i deleted", image_id)
        else:
            cache.set(f"image:{image_id}:logo", logo)

    if processed["empty_streetview"]:
        image.delete()
        task_logger.info("Empty streetview: image #%i deleted", image_id)

    if processed["textual"]:
        image.delete()

    if "text" in processed:
        cache.set(f"image:{image_id}:text", processed["text"])

    cache.set(processed_key, True)


def process_image(image):
    if vision.CLIENT:
        cloud_vision_process.delay(image.pk)


@receiver(post_save, sender=Proposal, dispatch_uid="process_new_proposal")
def proposal_hook(**kwargs):
    if kwargs["created"]:
        process_proposal(kwargs["instance"])


@receiver(post_save, sender=Document, dispatch_uid="process_new_document")
def document_hook(**kwargs):
    if kwargs["created"]:
        process_document_sync.delay(kwargs["instance"].pk)

