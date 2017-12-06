"""General utilities shared across all applications.

"""
from datetime import datetime
import inspect
import re
from urllib.parse import urljoin

from django.conf import settings


protocol = "https" if settings.IS_PRODUCTION else "http"

def make_absolute_url(path):
    if re.match(r"^https?://", path):
        return path

    return urljoin(f"{protocol}://{settings.SERVER_DOMAIN}", path)


def today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
