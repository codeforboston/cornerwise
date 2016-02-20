from cornerwise import celery_app
from .models import Project
from .importers.register import Importers

import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="project.pull_updates")
def pull_updates(since=None):
    if not since:
        # Calculate the last time the project scraper ran
        pass

    projects = []

    for importer in Importers:
        projects += importer.updated_since(since)

    created = []

    for project in projects:
        created.append(Project.create_from_dict(project))

    return created
