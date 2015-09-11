from django.apps import AppConfig
from datetime import datetime

class ProposalConfig(AppConfig):
    def ready(self):
        from . import tasks

        tasks.scrape_reports_and_decisions.delay(datetime(2015, 6, 1))
