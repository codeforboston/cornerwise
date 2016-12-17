from .celery import app as celery_app
from . import logging


__all__ = ["celery_app"]
