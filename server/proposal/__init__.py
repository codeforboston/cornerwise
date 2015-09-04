from django.apps import AppConfig
from datetime import datetime

from . import tasks

class ProposalConfig(AppConfig):
    def ready(self):
        tasks.scrape_reports_and_decisions.delay(datetime(2015, 6, 1))
