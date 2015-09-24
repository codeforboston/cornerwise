from datetime import datetime
import logging
import os
import shutil
import subprocess
from urllib import parse, request

from djcelery.models import PeriodicTask
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.utils import IntegrityError

from .models import Proposal, Attribute, Event, Document, Image
from . import extract
from cornerwise import celery_app
from scripts import scrape, arcgis, gmaps, images

logger = logging.getLogger(__name__)

def last_run():
    "Determine the date and time of the last run of the task."
    try:
        scrape_task = PeriodicTask.objects.get(name="scrape-permits")
        return scrape_task.last_run_at
    except PeriodicTask.DoesNotExist:
        return None

def extension(path):
    return path.split(os.path.extsep)[-1].lower()

def published_date(path):
    # TODO: Handle other document types
    ext = extension(path)

    if ext == "pdf":
        proc = subprocess.Popen(["pdfinfo", path],
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        out, err = proc.communicate()
        m = re.search(r"CreationDate:\s+(.*?)\n", out.decode("UTF-8"))

        if m:
            datestr = m.group(1)
            return datetime.strptime(datestr, "%c")

    return datetime.fromtimestamp(os.path.getmtime(path))


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

                doc.save()

    return proposal


@celery_app.task(name="proposal.fetch_document")
def fetch_document(doc):
    """Copy the given document (proposal.models.Document) to a local
    directory.
    """
    url = doc.url
    url_components = parse.urlsplit(url)
    filename = os.path.basename(url_components.path)
    path = os.path.join(settings.MEDIA_ROOT, "doc",
                        str(doc.pk),
                        filename)

    # Ensure that the intermediate directories exist:
    pathdir = os.path.dirname(path)
    os.makedirs(pathdir, exist_ok=True)

    with request.urlopen(url) as resp, open(path, "wb") as out:
        shutil.copyfileobj(resp, out)
        doc.document = path
        doc.save()

def fetch_all_documents():
    """Fetches all documents that have not been copied to the local
    filesystem."""
    docs = Document.objects.filter(document__isnull=True)

    for doc in docs:
        #fetch_document.delay(doc)
        fetch_document(doc)

@celery_app.task(name="proposal.extract_content")
def extract_content(doc, encoding="ISO-8859-9"):
    """If the given document (proposal.models.Document) has been copied to
    the local filesystem, extract its images to a subdirectory of the
    document's directory (docs/<doc id>/images). Extracts the text
    content to docs/<doc id>/content.txt.

    """
    docfile = doc.document

    if not docfile:
        logger.error("Document has not been copied to the local filesystem.")
        return

    try:
        path = docfile.path
    except:
        path = docfile.name

    if not os.path.exists(path):
        logger.error("Document %s is not where it says it is: %s",
                     doc.pk, path)
        return

    images_dir = os.path.join(os.path.dirname(path), "images")
    os.makedirs(images_dir, exist_ok=True)

    images_pattern = os.path.join(images_dir, "image")

    logger.info("Extracting images to '%s'", images_dir)
    status = subprocess.call(["pdfimages", "-png", "-tiff", "-j", "-jp2",
                              path, images_pattern])

    if status:
        logger.warn("pdfimages failed with exit code %i", status)
    else:
        # Do stuff with the images in the directory
        for image_name in os.listdir(images_dir):
            image_path = os.path.join(images_dir, image_name)

            if not images.is_interesting(image_path):
                # Delete 'uninteresting' images
                os.unlink(image_path)
                continue

            image = Image(proposal=doc.proposal,
                          document=doc)
            image.image = image_path
            #image.set_image_path(image_path)

            try:
                image.save()
            except IntegrityError:
                # This can occur if the image has already been fetched
                # and associated with the Proposal.
                pass

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
    else:
        # Do stuff with the contents of the file.
        # Possibly perform some rudimentary scraping?
        doc.fulltext = text_path
        doc.encoding = encoding
        doc.save()

def generate_doc_thumbnail(doc):
    ""
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
        logger.error("Failed to generate PDF for document %s: %s",
                     path, err)
    else:
        doc.thumbnail = out_prefix + os.path.extsep + "jpg"
        #doc.thumbnail = util.media_path(path)
        doc.save()


@celery_app.task(name="proposal.generate_thumbnail")
def generate_thumbnail(image, replace=False):
    "Generate an image thumbnail."
    if image.thumbnail and os.path.exists(image.thumbnail.name):
        logger.info("Thumbnail already exists (%s)", image.thumbnail.name)
        return

    try:
        thumbnail_path = images.make_thumbnail(image.image.name,
                                               fit=settings.THUMBNAIL_DIM)
    except Exception as err:
        logger.error(err)
        return

    #image.set_thumbnail_path(thumbnail_path)
    image.thumbnail = thumbnail_path
    image.save()

def generate_thumbnails(replace=False):
    "Generate thumbnails for all Images in the database."
    images = Image.objects.filter(thumbnail=None)
    for image in images:
        generate_thumbnail(image, replace=replace)


def extract_all_content():
    "Extract the contents of all documents."
    docs = Document.objects.all()

    for doc in docs:
        extract_content(doc)

@celery_app.task(name="proposal.add_doc_attributes")
@transaction.atomic
def add_doc_attributes(doc):
    properties = extract.get_properties(doc)
    for name, value in properties.items():
        logger.info("Adding %s attribute", name)
        attr = Attribute(proposal=doc.proposal,
                         name=name,
                         text_value=value)
        attr.save()

def process_document(doc):
    """
    Run all tasks on a Document.
    """
    fetch_document(doc)
    extract_content(doc)
    add_doc_attributes(doc)

    for image in Image.objects.filter(document=doc):
        generate_thumbnail(image)

    generate_doc_thumbnail(doc)


@celery_app.task(name="proposal.scrape_reports_and_decisions")
@transaction.atomic
def scrape_reports_and_decisions(since=None, page=None, everything=False,
                                 coder_type=settings.GEOCODER):
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
