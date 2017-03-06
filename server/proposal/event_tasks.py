from datetime import datetime, timedelta

import pytz

from celery.utils.log import get_task_logger
from cornerwise import celery_app

from .importers.register import EventImporters
from .models import Event, Proposal

logger = get_task_logger(__name__)


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
            all_events = Event.objects.filter(
                region_name=importer.region_name).order_by("-created")
            try:
                last_event = all_events[0]
                if not last_event.created.tzinfo:
                    since = pytz.utc.localize(last_event.created)
            except IndexError:
                pass

        importer_events = [
            Event.make_event(ejson) for ejson in importer.updated_since(since)
        ]
        events += importer_events

        logger.info("Fetched %i events from %s",
                    len(importer_events), type(importer).__name__)

    return [event.pk for event in events]
