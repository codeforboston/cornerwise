from cornerwise import celery_app
from scripts import socrata
from .importers.register import Importers

import logging

logging.getLogger(__name__)


@celery_app.task(name="project.pull_updates")
def pull_updates(since=None):
    if not since:
        # Calculate the last time the project scraper ran
        pass

    projects = []

    for importer in Importers:
        projects += importer.updated_since(since)
    
