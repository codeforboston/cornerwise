from datetime import datetime, timedelta
import os
import shutil
import subprocess
from urllib import parse, request

from dateutil.parser import parse as dt_parse
import celery
from celery.utils.log import get_task_logger

from django.conf import settings
from django.db import transaction
from django.db.utils import DataError, IntegrityError

from .models import Proposal, Attribute, Event, Document, Image
from utils import extension, normalize
from . import extract
from . import utils as proposal_utils
from .importers.register import Importers
from cornerwise import celery_app
from scripts import arcgis, gmaps, street_view
from scripts import pdf
from scripts.images import is_interesting, make_thumbnail

from shared import files_metadata

logger = get_task_logger(__name__)


@celery_app.task(name="proposal.fetch_document")
def fetch_document(doc_id):
    """Copy the given document (proposal.models.Document) to a local
    directory.
    """
    doc = Document.objects.get(pk=doc_id)
    url = doc.url

    if doc.document and os.path.exists(doc.document.path):
        # Has the document been updated?
        updated = proposal_utils.last_modified(doc.url)
        # No?  Then we're good.
        if not updated or updated <= doc.published:
            return doc.pk

        # TODO Special handling of updated documents

    url_components = parse.urlsplit(url)
    ext = extension(os.path.basename(url_components.path))
    filename = "download.%s" % ext
    path = os.path.join(settings.MEDIA_ROOT, "doc",
                        str(doc.pk),
                        filename)

    # Ensure that the intermediate directories exist:
    pathdir = os.path.dirname(path)
    os.makedirs(pathdir, exist_ok=True)

    logger.info("Fetching Document #%i", doc.pk)
    with request.urlopen(url) as resp, open(path, "wb") as out:
        shutil.copyfileobj(resp, out)
        doc.document = path

        logger.info("Copied Document #%i to %s", doc.pk, path)

        file_published = files_metadata.published_date(path)

        if file_published:
            doc.published = file_published
        elif "Last-Modified" in resp.headers:
            doc.published = dt_parse(resp.headers["Last-Modified"])

        doc.save()

    return doc.pk


@celery_app.task(name="proposal.extract_text")
def extract_text(doc_id, encoding="ISO-8859-9"):
    """If a document is a PDF that has been copied to the filesystem, extract its
    text contents to a file and save the path of the text document.

    :param doc: proposal.models.Document object

    :returns: The same document

    """
    doc = Document.objects.get(pk=doc_id)
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
        logger.error("Failed to extract text from %s", path)
    else:
        logger.info("Extracted text from Document #%i to %s.",
                    doc.pk, doc.fulltext)
        doc.fulltext = text_path
        doc.encoding = encoding
        doc.save()

        return doc.pk


@celery_app.task(name="proposal.extract_images")
def extract_images(doc_id):
    """If the given document (proposal.models.Document) has been copied to
    the local filesystem, extract its images to a subdirectory of the
    document's directory (docs/<doc id>/images).

    :param doc: proposal.models.Document object with a corresponding PDF
    file that has been copied to the local filesystem

    :returns: A list of proposal.model.Image objects

    """
    doc = Document.objects.get(pk=doc_id)
    docfile = doc.document

    if not docfile:
        logger.error("Document has not been copied to the local filesystem.")
        return []

    path = docfile.path

    if not os.path.exists(path):
        logger.error("Document %s is not where it says it is: %s",
                     doc.pk, path)
        return []

    images_dir = os.path.join(os.path.dirname(path), "images")
    os.makedirs(images_dir, exist_ok=True)

    logger.info("Extracting images to '%s'", images_dir)
    image_paths = pdf.extract_images(path, dirname=images_dir)

    images = []
    # Do stuff with the images in the directory
    for image_name in image_paths:
        image_path = os.path.join(images_dir, image_name)

        if not is_interesting(image_path):
            # Delete 'uninteresting' images
            os.unlink(image_path)
            continue

        image = Image(proposal=doc.proposal,
                      document=doc)
        image.image = image_path
        images.append(image)

        try:
            image.save()
        except IntegrityError:
            # This can occur if the image has already been fetched
            # and associated with the Proposal.
            pass

    logger.info("Extracted %i image(s) from %s.", len(images), path)

    return [image.pk for image in images]


@celery_app.task(name="proposal.add_street_view")
def add_street_view(proposal_id):
    api_key = getattr(settings, "GOOGLE_API_KEY")
    secret = getattr(settings, "GOOGLE_STREET_VIEW_SECRET")

    proposal = Proposal.objects.get(pk=proposal_id)

    if api_key:
        location = "{0.address}, {0.region_name}".format(proposal)
        url = street_view.street_view_url(location, api_key,
                                          secret=secret)
        try:
            # Check that there is not already a Street View image associated
            # with this proposal:
            if not proposal.images\
                           .filter(source="google_street_view")\
                           .exists():
                image = proposal.images.create(url=url,
                                               skip_cache=True,
                                               source="google_street_view",
                                               priority=1)
                return image
        except IntegrityError:
            logger.warning("Image with that URL already exists: %s", url)
        except DataError:
            logger.error("Image could not be saved.  Was the URL too long? %s",
                         url)

    else:
        logger.warn("Add a local_settings file with your Google API key " +
                    "to add Street View images.")


@celery_app.task(name="proposal.generate_doc_thumbnail")
def generate_doc_thumbnail(doc_id):
    "Generate a Document thumbnail."
    doc = Document.objects.get(pk=doc_id)
    docfile = doc.document

    if not docfile:
        logger.error("Document has not been copied to the local filesystem")
        return

    path = docfile.name

    # TODO: Dispatch on extension. Handle other common file types
    if extension(path) != "pdf":
        logger.warn("Document %s does not appear to be a PDF.", path)
        return

    out_prefix = os.path.join(os.path.dirname(path), "thumbnail")

    proc = subprocess.Popen(["pdftoppm", "-jpeg", "-singlefile",
                             "-scale-to", "200", path, out_prefix],
                            stderr=subprocess.PIPE)
    _, err = proc.communicate()

    if proc.returncode:
        logger.error("Failed to generate thumbnail for document %s: %s",
                     path, err)
        raise Exception("Failed for document %s" % doc.pk)
    else:
        thumb_path = out_prefix + os.path.extsep + "jpg"
        logger.info("Generated thumbnail for Document #%i: '%s'",
                    doc.pk, thumb_path)
        doc.thumbnail = thumb_path
        doc.save()

        return thumb_path


@celery_app.task(name="proposal.fetch_image")
def fetch_image(image_id):
    image = Image.objects.get(pk=image_id)
    url = image.url

    if url:
        components = parse.urlsplit(url)
        ext = extension(os.path.basename(components.path))
        filename = "image_%s.%s" % (image.pk, ext)
        path = os.path.join(settings.MEDIA_ROOT, "image", filename)
        with request.urlopen(url) as resp, open(path, "wb") as out:
            shutil.copyfileobj(resp, out)
            image.document = path

            image.save()

    return image


@celery_app.task(name="proposal.generate_thumbnail")
def generate_thumbnail(image_id, replace=False):
    """Generate an image thumbnail.

    :param image: A proposal.model.Image object with a corresponding
    image file on the local filesystem.

    :returns: Thumbnail path"""

    image = Image.objects.get(pk=image_id)
    thumbnail_path = image.thumbnail and image.thumbnail.name
    if thumbnail_path and os.path.exists(thumbnail_path):
        logger.info("Thumbnail already exists (%s)", image.thumbnail.name)
    else:
        if not image.image:
            logger.info("No local image for Image #%s", image.pk)
            return

        try:
            thumbnail_path = make_thumbnail(image.image.name,
                                            fit=settings.THUMBNAIL_DIM)
        except Exception as err:
            logger.error(err)
            return

        logger.info("Generate thumbnail for Image #%i: %s", image.pk,
                    thumbnail_path)
        image.thumbnail = thumbnail_path
        image.save()

    return thumbnail_path


@celery_app.task(name="proposal.add_doc_attributes")
@transaction.atomic
def add_doc_attributes(doc_id):
    doc = Document.objects.get(pk=doc_id)
    doc_json = proposal_utils.doc_info(doc)
    properties = extract.get_properties(doc_json)

    for name, value in properties.items():
        logger.info("Adding %s attribute", name)
        published = doc.published or datetime.now()
        handle = normalize(name)

        try:
            attr = Attribute.objects.get(proposal=doc.proposal,
                                         handle=handle)
        except Attribute.DoesNotExist:
            attr = Attribute(proposal=doc.proposal,
                             name=name,
                             handle=normalize(name),
                             published=published)
            attr.set_value(value)
        else:
            # TODO: Either mark the old attribute as stale and create a
            # new one or create a record that the value has changed
            if published > attr.published:
                attr.clear_value()
                attr.set_value(value)

        attr.save()

    add_doc_events(doc_id, properties)

    return doc


@celery_app.task(name="proposal.add_doc_events")
def add_doc_events(doc_id, properties):
    doc = Document.objects.get(pk=doc_id)
    if not doc.proposal:
        return

    doc_json = proposal_utils.doc_info(doc)

    # Find events and create them:
    events = extract.get_events(doc_json, properties)

    if not events:
        return

    event = None
    for e in events:
        event = None
        try:
            event = Event.objects.get(title=e["title"],
                                      date=e["date"])

        except Event.DoesNotExist:
            # Create a new event:
            event = Event(title=e["title"],
                          date=e["date"])
        except KeyError as kerr:
            logger.error("Missing required key in extracted event: %s",
                         kerr.args)

    if event:
        event.save()
        event.proposals.add(doc.proposal)

    return properties


@celery_app.task(name="proposal.generate_thumbnails")
def generate_thumbnails(image_ids):
    return generate_thumbnail.map(image_ids)()


@celery_app.task(name="proposal.process_document")
def process_document(doc_id):
    """
    Run all tasks on a Document.
    """
    (fetch_document.s(doc_id) |
     celery.group((extract_images.s() | generate_thumbnails.s()),
                  generate_doc_thumbnail.s(),
                  extract_text.s() | add_doc_attributes.s()))()


@celery_app.task(name="proposal.process_documents")
def process_documents(doc_ids=None):
    if not doc_ids:
        doc_ids = Document.objects.filter(document="").values_list("id", flat=True)

    return process_document.map(doc_ids)()


@celery_app.task(name="proposal.process_proposal")
def process_proposal(proposal_id):
    "Perform additional processing on proposals."
    # Create a Google Street View image for each proposal:
    add_street_view(proposal_id)

    return proposal_id


@celery_app.task(name="proposal.fetch_proposals")
@transaction.atomic
def fetch_proposals(since=None, coder_type=settings.GEOCODER,
                    importers=Importers):
    """
    Task that scrapes the reports and decisions page
    """
    if coder_type == "google":
        geocoder = gmaps.GoogleGeocoder(settings.GOOGLE_API_KEY)
        geocoder.bounds = settings.GEO_BOUNDS
        geocoder.region = settings.GEO_REGION
    else:
        geocoder = arcgis.ArcGISCoder(settings.ARCGIS_CLIENT_ID,
                                      settings.ARCGIS_CLIENT_SECRET)

    # TODO: If `since` is not provided explicitly, we should probably determine
    # the appropriate date on a per-importer basis.
    if since:
        since = datetime.fromtimestamp(since)
    else:
        latest_proposal = Proposal.objects.latest()
        if latest_proposal:
            since = latest_proposal.updated

        if not since:
            # If there is no record of a previous run, fetch
            # proposals posted since the previous Monday.
            now = datetime.now().replace(hour=0, minute=0,
                                         second=0, microsecond=0)
            since = now - timedelta(days=7 + now.weekday())

    proposals_json = []
    for importer in importers:
        importer_name = type(importer).__name__
        try:
            found = list(importer.updated_since(since, geocoder))
        except Exception as err:
            logger.warning("Error in importer: %s - %s", importer_name, err)
            continue

        logger.info("Fetched %i proposals from %s",
                    len(found), type(importer).__name__)
        proposals_json += found

    proposals = []

    for p_dict in proposals_json:
        try:
            (is_new, p) = Proposal.create_or_update_proposal_from_dict(p_dict)
            p.save()
            proposals.append(p)
        except Exception as exc:
            logger.error("Could not create proposal from dictionary: %s",
                         p_dict)
            logger.error("%s", exc)

    return proposals


@celery_app.task(name="proposal.pull_updates")
def pull_updates(since=None, importers_filter=None):
    importers = Importers
    if importers_filter:
        name = importers_filter.lower()
        importers = [imp for imp in importers if name in imp.region_name.lower()]

    proposals = fetch_proposals(since, importers=importers)
    proposal_ids = [p.id for p in proposals]
    process_proposal.map(proposal_ids)()
    doc_ids = Document.objects.filter(proposal_id__in=proposal_ids)\
                              .values_list("id", flat=True)
    process_document.map(doc_ids)()

    return proposals
