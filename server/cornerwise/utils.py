from django.conf import settings

from datetime import datetime


protocol = "https" if settings.IS_PRODUCTION else "http"

def make_absolute_url(path):
    return "{protocol}://{domain}{path}".format(protocol=protocol,
                                                domain=settings.SERVER_DOMAIN,
                                                path=path)


def today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
