from django.apps import AppConfig


class ProposalConfig(AppConfig):
    name = "proposal"

    def ready(self):
        # Register tasks with Celery:
        from . import tasks

