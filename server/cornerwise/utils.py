from django.conf import settings


def make_absolute_url(path):
    return "http://{domain}{path}".format(domain=settings.SERVER_DOMAIN,
                                          path=path)
