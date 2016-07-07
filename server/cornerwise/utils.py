from django.conf import settings

from datetime import datetime
import re


protocol = "https" if settings.IS_PRODUCTION else "http"

def make_absolute_url(path):
    if re.match(r"^https?://", path):
        return path

    return "{protocol}://{domain}{path}".format(protocol=protocol,
                                                domain=settings.SERVER_DOMAIN,
                                                path=path)


def today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
