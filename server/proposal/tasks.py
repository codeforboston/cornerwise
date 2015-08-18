from djcelery.models import PeriodicTask
from django.contrib.gis.geos import Point

from .models import Proposal, Event, Document, DoesNotExist
from citydash import celery_app
from scripts import scrape

def last_run():
    "Determine the date and time of the last run of the task."
    scrape_task = PeriodicTask.objects.find(name="scrape-permits")
    return scrape_task.last_run_at

def create_proposal_from_json(p_dict):
    "Constructs a Proposal from a dictionary."
    try:
        proposal = Proposal.objects.get(case_number=["caseNumber"])

            # TODO: We should track changes to a proposal's status over
            # time. This may mean full version-control, with something
            # like django-reversion or with a hand-rolled alternative.
    except DoesNotExist:
        proposal = Proposal(case_number=p_dict["caseNumber"])

        proposal.address = "{} {}".format(p_dict["number"],
                                          p_dict["street"])
        proposal.location = Point(p_dict["long"], p_dict["lat"])
        proposal.summary = "No summary available"
        proposal.description = ""
        # This should not be hardcoded
        proposal.source = "http://www.somervillema.gov/departments/planning-board/reports-and-decisions"

        # For now, we assume that if there are one or more documents
        # linked in the 'decision' page, the proposal is 'complete'.
        # Note that we don't have insight into whether the proposal was
        # approved!
        is_complete = bool(p_dict["decisions"]["links"])

        # Create associated documents:
        for field, val in p_dict.items():
            if not isinstance(val, dict) or not val.get("links"):
                continue

            for link in val["links"]:
                doc = ProposalDocument(url=link["url"],
                                       title=link["title"],
                                       field=field)
                proposal.document_set.add(doc)

        return proposal


@celery_app.task
def scrape_reports_and_decisions(since=None):
    if not since:
        since = last_run()

    # Array of dicts:
    proposals_json = scrape.get_proposals_since(since)
    proposals = []

    for p_dict in proposals_json:
        p = create_proposal_from_json(p_dict)
        p.save()
        proposals.append(p)
