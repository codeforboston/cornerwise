import logging
import os
import shutil
from urllib import parse, request

from djcelery.models import PeriodicTask
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.utils import IntegrityError

from .models import Proposal, Event, Document
from cornerwise import celery_app
from scripts import scrape, arcgis, gmaps

logger = logging.getLogger(__name__)

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
        return
    proposal.summary = "No summary available"
    proposal.description = ""
    # This should not be hardcoded
    proposal.source = "http://www.somervillema.gov/departments/planning-board/reports-and-decisions"

    # For now, we assume that if there are one or more documents
    # linked in the 'decision' page, the proposal is 'complete'.
    # Note that we don't have insight into whether the proposal was
    # approved!
    is_complete = bool(p_dict["decisions"]["links"])

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


@celery_app.task
def fetch_document(doc):
    """Copy the given document (proposal.models.Document) to a local
    directory.
    """
    url = doc.url
    url_components = parse.urlsplit(url)
    filename = os.path.basename(url_components.path)
    path = os.path.join(settings.STATIC_ROOT, "doc",
                        str(doc.proposal.pk),
                        filename)

    # Ensure that the intermediate directories exist:
    pathdir = os.path.dirname(path)
    os.makedirs(pathdir, exist_ok=True)

    with request.urlopen(url) as resp, open(path, "wb") as out:
        shutil.copyfileobj(resp, out)
        doc.document = path
        doc.save()


@celery_app.task
@transaction.atomic
def scrape_reports_and_decisions(since=None, coder_type="google"):
    if not since:
        # If there was no last run, the scraper will fetch all
        # proposals.
        since = last_run()

    if coder_type == "google":
        geocoder = gmaps.GoogleGeocoder(settings.GOOGLE_API_KEY)
    else:
        geocoder = arcgis.ArcGISCoder(settings.ARCGIS_CLIENT_ID,
                                      settings.ARCGIS_CLIENT_SECRET)

    # Array of dicts:
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
