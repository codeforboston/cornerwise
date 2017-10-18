from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from datetime import datetime, timedelta
import json
from urllib.request import urlopen

from proposal.models import Importer

import jsonschema


class Command(BaseCommand):
    help = "Validate that the importers conform to the JSON schema"

    def handle(self, *args, **options):
        now = datetime.now() - timedelta(days=30)
        for importer in Importer.objects.all():
            try:
                importer.validate(now)
            except jsonschema.exceptions.ValidationError as err:
                self.stdout.write(f"Error in {importer}: {err}")
