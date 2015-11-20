from django.apps import AppConfig

class ProjectConfig(AppConfig):
    name = "project"

    def ready(self):
        # Register tasks with Celery:
        #from . import tasks
        pass
