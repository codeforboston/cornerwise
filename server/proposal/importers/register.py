from django.conf import settings

# Import your importers:
from . import somervillema

socrata_token = getattr(settings, "SOCRATA_APP_TOKEN", None)

Importers = [
    somervillema.SomervilleImporter()
]

EventImporters = [
    somervillema.EventsImporter()
]

if socrata_token:
    from . import cambridgema
    Importers.append(cambridgema.CambridgeImporter(socrata_token))
