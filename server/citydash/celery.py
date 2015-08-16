import os

from celery import Celery

from scripts import scrape


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citydash.settings')
from django.conf import settings

app = Celery("tasks")
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
