from __future__ import unicode_literals

from django.core.serializers import deserialize
from django.db import migrations, models

import json
from os import path


fixture_path = path.abspath(path.join(path.dirname(__file__), "../fixtures/importers.json"))

def load_fixture(apps, schema_editor):
    with open(fixture_path) as fixt:
        importers_json = json.load(fixt)
    Importer = apps.get_model("proposal", "Importer")

    for importer_dict in importers_json:
        importer = Importer(pk=importer_dict["pk"],
                            **{f: importer_dict["fields"][f]
                               for f in ("name", "region_name", "url")})
        importer.save()


def unload_fixture():
    Importer = apps.get_model("proposal", "Importer")
    with open(fixture_path) as fixt:
        importers_json = json.load(fixt)
    Importer.objects.filter(pk__in=[ij["pk"] for ij in importers_json])


class Migration(migrations.Migration):
    dependencies = [
        ('proposal', '0013_nullable_last_run'),
    ]

    operations = [
        migrations.RunPython(load_fixture, unload_fixture)
    ]
