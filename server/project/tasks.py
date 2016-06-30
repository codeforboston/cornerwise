from django.db.utils import IntegrityError
from datetime import datetime
from cornerwise import celery_app
from project.models import Project
from project.importers.register import Importers

import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="project.pull_updates")
def pull_updates(since=None):
    if since:
        since = datetime.fromtimestamp(since)
    else:
        # Calculate the last time the project scraper ran
        pass

    projects = []

    for importer in Importers:
        projects += importer.updated_since(since)

    created = []

    for project in projects:
        try:
            created.append(Project.create_from_dict(project))
        except IntegrityError as ierr:
            logger.error("Could not create project '%s': %s",
                         project["name"], ierr)

    return created
