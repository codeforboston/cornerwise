from datetime import datetime, timedelta

import pytz

from celery.utils.log import get_task_logger
from cornerwise import celery_app

from .importers.register import EventImporters
from .models import Event, Proposal

logger = get_task_logger(__name__)


def make_event(event_json):
    """
    event_json should have the following fields:
    - title (str) - Name of the event
    - date (datetime with local timezone) - When will the event occur?
    - posted (datetime with UTC timezone)
    - cases - A list of case numbers
    - region_name
    - duration (timedelta, optional) - how long will the event last?
    """
    try:
        event = Event.objects.get(title=event_json["title"],
                                  date=event_json["date"],
                                  region_name=event_json["region_name"])
    except Event.DoesNotExist:
        kwargs = {
            k: event_json.get(k)
            for k in ("title", "date", "region_name", "duration")
        }
        event = Event(**kwargs)
        event.save()

    for case_number in event_json["cases"]:
        try:
            proposal = Proposal.objects.get(case_number=case_number)
            event.proposals.add(proposal)
        except Proposal.DoesNotExist:
            continue

    return event


@celery_app.task(name="proposal.pull_events")
def pull_events(since=None):
    """
    Runs all registered event importers.
    """
    if since:
        since = datetime.fromtimestamp(since)

    events = []
    for importer in EventImporters:
        if not since:
            last_event = Event.objects.filter(
                region_name=importer.region_name).order_by("-created")[0]
            since = pytz.utc.localize(last_event.created)

        importer_events = [
            make_event(ejson) for ejson in importer.updated_since(since)
        ]
        events += importer_events

        logger.info("Fetched %i proposals from %s",
                    len(importer_events), type(importer).__name__)

    return [event.pk for event in events]
