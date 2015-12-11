from cornerwise import celery_app
from scripts import socrata

from django.conf import settings

import logging

logging.getLogger(__name__)


def poll_socrata(since=None):
    api_token = getattr(settings, "SOCRATA_APP_TOKEN", None)
    api_secret = getattr(settings, "SOCRATA_APP_SECRET", None)

    if not api_token:
        logging.warning("Cannot scrape Socrata without an API token.")
        return

    json = socrata.do_get("data.somervillema.gov",
                          "wz6k-gm5k",
                          api_token)
    return json
