from django.conf import settings

from . import somervillema

socrata_token = getattr(settings, "SOCRATA_APP_TOKEN", None)

Importers = []

if socrata_token:
    Importers.append(somervillema.Importer(socrata_token))
