from django.conf import settings

from datetime import datetime


def make_absolute_url(path):
    return "http://{domain}{path}".format(domain=settings.SERVER_DOMAIN,
                                          path=path)


def today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
