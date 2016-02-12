from django.conf import settings

# Import your importers:
from . import somervillema

socrata_token = getattr(settings, "SOCRATA_APP_TOKEN", None)

Importers = [
    somervillema.Importer()
]

if socrata_token:
    from . import cambridgema
    Importers.append(cambridgema.Importer(socrata_token))
