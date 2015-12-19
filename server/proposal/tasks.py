from datetime import datetime, timedelta
import os
import shutil
import subprocess
from urllib import parse, request

import celery
from celery.utils.log import get_task_logger

from djcelery.models import PeriodicTask
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.utils import IntegrityError

from .models import Proposal, Attribute, Event, Document, Image
from utils import extension, normalize
from . import extract
from cornerwise import celery_app
from scripts import scrape, arcgis, gmaps, street_view
from scripts.images import is_interesting, make_thumbnail
from shared import files_metadata

logger = get_task_logger(__name__)

def last_run():
    "Determine the date and time of the last run of the task."
    try:
        scrape_task = PeriodicTask.objects.get(name="scrape-permits")
        return scrape_task.last_run_at
    except PeriodicTask.DoesNotExist:
        return None


def create_proposal_from_json(p_dict):
    "Constructs a Proposal from a dictionary."
    try:
        proposal = Proposal.objects.get(case_number=p_dict["caseNumber"])

        # TODO: We should track changes to a proposal's status over
        # time. This may mean full version-control, with something
        # like django-reversion, or with a hand-rolled alternative.
    except Proposal.DoesNotExist:
        proposal = Proposal(case_number=p_dict["caseNumber"])

    proposal.address = "{} {}".format(p_dict["number"],
                                      p_dict["street"])
    try:
        proposal.location = Point(p_dict["long"], p_dict["lat"])
    except KeyError:
        # If the dictionary does not have an associated location, do not
        # create a Proposal.
        return

    proposal.summary = p_dict.get("summary")
    proposal.description = p_dict.get("description")
    # This should not be hardcoded
    proposal.source = "http://www.somervillema.gov/departments/planning-board/reports-and-decisions"
    proposal.modified = p_dict["updatedDate"]

    # For now, we assume that if there are one or more documents
    # linked in the 'decision' page, the proposal is 'complete'.
    # Note that we don't have insight into whether the proposal was
    # approved!
    proposal.complete = bool(p_dict["decisions"]["links"])

    proposal.save()

    # Create associated documents:
    for field, val in p_dict.items():
        if not isinstance(val, dict) or not val.get("links"):
            continue

        for link in val["links"]:
            try:
                doc = proposal.document_set.get(url=link["url"])
            except Document.DoesNotExist:
                doc = Document(proposal=proposal)

                doc.url = link["url"]
                doc.title = link["title"]
                doc.field = field
                doc.published = p_dict["updatedDate"]

                doc.save()

    return proposal


@celery_app.task(name="proposal.fetch_document")
def fetch_document(doc, force=False):
    """Copy the given document (proposal.models.Document) to a local
    directory.
    """
    if not force and doc.document and os.path.exists(doc.document.path):
        return

    url = doc.url
    url_components = parse.urlsplit(url)
    ext = extension(os.path.basename(url_components.path))
    filename = "download.%s" % ext
    path = os.path.join(settings.MEDIA_ROOT, "doc",
                        str(doc.pk),
                        filename)

    # Ensure that the intermediate directories exist:
    pathdir = os.path.dirname(path)
    os.makedirs(pathdir, exist_ok=True)

    with request.urlopen(url) as resp, open(path, "wb") as out:
        shutil.copyfileobj(resp, out)
        doc.document = path

        file_published = files_metadata.published_date(path)

        if file_published:
            doc.published = file_published

        doc.save()

    return doc


@celery_app.task(name="proposal.extract_text")
def extract_text(doc, encoding="ISO-8859-9"):
    """If a document is a PDF, extract its text contents to a file and save
the path of the text document.

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
        logger.error("Failed to extract text from {doc}".\
                     format(doc=path))
        # TODO: Correct way to signal a 'hard' failure that will break
        # this chain of subtasks.
    else:
        # Do stuff with the contents of the file.
        # Possibly perform some rudimentary scraping?
        doc.fulltext = text_path
        doc.encoding = encoding
        doc.save()

        return doc


@celery_app.task(name="proposal.extract_images")
def extract_images(doc):
    """If the given document (proposal.models.Document) has been copied to
    the local filesystem, extract its images to a subdirectory of the
    document's directory (docs/<doc id>/images). Extracts the text
    contents to docs/<doc id>/text.txt.

    :param doc: proposal.models.Document object with a corresponding PDF
    file that has been copied to the local filesystem

    :returns: A list of proposal.model.Image objects

    """
    # TODO: Break this into smaller subtasks
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

    images_pattern = os.path.join(images_dir, "image")

    logger.info("Extracting images to '%s'", images_dir)
    status = subprocess.call(["pdfimages", "-png", "-tiff", "-j", "-jp2",
                              path, images_pattern])

    images = []
    if status:
        logger.warn("pdfimages failed with exit code %i", status)
    else:
        # Do stuff with the images in the directory
        for image_name in os.listdir(images_dir):
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

    return images


@celery_app.task(name="proposal.add_street_view")
def add_street_view(proposal):
    api_key = getattr(settings, "GOOGLE_API_KEY")
    secret = getattr(settings, "GOOGLE_STREET_VIEW_SECRET")

    if api_key:
        location = "{0.address}, {0.region_name}".format(proposal)
        url = street_view.street_view_url(location, api_key,
                                          secret=secret)
        try:
            if not proposal.images\
                           .filter(source="google_street_view")\
                           .exists():
                image = proposal.images.create(url=url,
                                           skip_cache=True,
                                               source="google_street_view",
                                               priority=1)
                return image
        except IntegrityError as ie:
            logger.warning("Image with that URL already exists")

    else:
        logger.warning("Add a local_settings file with your Google API key.")


@celery_app.task(name="proposal.generate_doc_thumbnail")
def generate_doc_thumbnail(doc):
    "Generate a Document thumbnail."

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
        doc.thumbnail = thumb_path
        doc.save()

        return thumb_path


@celery_app.task(name="proposal.fetch_image")
def fetch_image(image):
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
def generate_thumbnail(image, replace=False):
    """Generate an image thumbnail.

    :param image: A proposal.model.Image object with a corresponding
    image file on the local filesystem.

    :returns: Thumbnail path"""

    thumbnail_path = image.thumbnail and image.thumbnail.name
    if os.path.exists(thumbnail_path):
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

        image.thumbnail = thumbnail_path
        image.save()

    return thumbnail_path


@celery_app.task(name="proposal.add_doc_attributes")
@transaction.atomic
def add_doc_attributes(doc):
    properties = extract.get_properties(doc)

    for name, value in properties.items():
        logger.info("Adding %s attribute", name)
        published = doc.published or datetime.now()
        handle = normalize(name)

        try:
            attr = Attribute.objects.get(proposal=doc.proposal,
                                         handle=handle)
        except Attribute.DoesNotExist as _:
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

    add_doc_events(doc, properties)


@celery_app.task(name="proposal.add_doc_events")
def add_doc_events(doc, properties):
    if not doc.proposal:
        return

    # Find events and create them:
    events = extract.get_events(doc, properties)

    if not events:
        return

    event = None
    for e in events:
        event = None
        try:
            event = Event.objects.get(title=e["title"],
                                      date=e["date"])

        except Event.DoesNotExist as dne:
            event = Event(title=e["title"],
                          date=e["date"])
        except KeyError as kerr:
            logger.error("Missing required key in extracted event:",
                         kerr.args)

    if event:
        event.save()
        event.proposals.add(doc.proposal)

    return properties


@celery_app.task(name="proposal.generate_thumbnails")
def generate_thumbnails(images):
    return generate_thumbnail.map(images)()


@celery_app.task(name="proposal.process_document")
def process_document(doc):
    """
    Run all tasks on a Document.
    """
    (fetch_document.s(doc) |
     celery.group((extract_images.s() | generate_thumbnails.s()),
                  generate_doc_thumbnail.s(),
                  extract_text.s() | add_doc_attributes.s(),
                  add_doc_events.s()))()


@celery_app.task(name="proposal.process_documents")
def process_documents(docs=None):
    if not docs:
        docs = Document.objects.filter(document="")

    return process_document.map(docs)()


@celery_app.task(name="proposal.process_proposals")
def process_proposals(proposals):
    "Perform additional processing on proposals."
    add_street_view.map(proposals)


@celery_app.task(name="proposal.scrape_reports_and_decisions")
@transaction.atomic
def scrape_reports_and_decisions(since=None, page=None,
                                 coder_type=settings.GEOCODER):
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

    if page is not None:
        proposals_json = scrape.get_proposals_for_page(page, geocoder)
    else:
        if not since:
            # If there was no last run, the scraper will fetch all
            # proposals.
            since = last_run()

            if not since:
                # If there is no record of a previous run, fetch
                # proposals posted since the previous Monday.
                now = datetime.now().replace(hour=0, minute=0,
                                             second=0, microsecond=0)
                since = now - timedelta(days=7 + now.weekday())

        proposals_json = scrape.get_proposals_since(dt=since, geocoder=geocoder)

    proposals = []

    for p_dict in proposals_json:
        p = create_proposal_from_json(p_dict)

        if p:
            p.save()
            proposals.append(p)
        else:
            logger.error("Could not create proposal from dictionary:",
                         p_dict)

    return proposals

def run_tasks():
    return (scrape_reports_and_decisions.s() |
            process_document.s())()
