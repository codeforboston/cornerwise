from django.apps import AppConfig
from datetime import datetime

class ProposalConfig(AppConfig):
    name = "proposal"

    def ready(self):
        # Register tasks with Celery:
        from . import tasks
