from django.conf import settings

from .somervillema import SomervilleProjectImporter


socrata_token = getattr(settings, "SOCRATA_APP_TOKEN", None)

Importers = []

if socrata_token:
    Importers.append(SomervilleProjectImporter(socrata_token))
