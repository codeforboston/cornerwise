from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from collections import defaultdict
from datetime import datetime, timedelta
import json
from urllib.request import urlopen

from proposal.models import Importer, get_importer_schema

from jsonschema import Draft4Validator


def schema_path_str(path):
    return "".join(f".{c}" if isinstance(c, str) else f"[{c}]" for c in path)


class Command(BaseCommand):
    help = "Validate that the importers conform to the JSON schema"

    def handle(self, *args, **options):
        err = lambda m: self.stderr.write(self.style.ERROR(m) + "\n")
        succ = lambda m: self.stdout.write(self.style.SUCCESS(m) + "\n")
        when = datetime.now() - timedelta(days=30)
        validator = Draft4Validator(get_importer_schema())

        for importer in Importer.objects.all():
            errors = defaultdict(list)
            for error in validator.iter_errors(importer.updated_since(when)):
                errors[schema_path_str(error.absolute_schema_path)].append(error)

            if errors:
                err(f"{len(errors)} error(s) in {importer}:")
                for path, errs in errors.items():
                    error = errs[0]
                    repeats = f" ({len(errs)} repeats)" if len(errs) > 1 else ""
                    err(f"at {path}{repeats}:\n{error.message}\n")
            else:
                succ(f"{importer} validated successfully!")
