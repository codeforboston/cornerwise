from django.conf import settings

# Import your importers:
from . import cambridgema
from . import somervillema


Importers = [
    somervillema.Importer()
]
