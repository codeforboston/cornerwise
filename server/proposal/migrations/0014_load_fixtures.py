from __future__ import unicode_literals

from django.core.serializers import deserialize
from django.db import migrations, models

import json
from os import path


fixture_path = path.abspath(path.join(path.dirname(__file__), "../fixtures/importers.json"))

def with_importers(fn):
    def wrapped_fn(*args):
        with open(fixture_path) as fix:
            return fn(deserialize("json", fix, ignorenonexistent=True))
    return wrapped_fn


@with_importers
def load_fixture(importers):
    for importer in importers:
        importer.save()


@with_importers
def unload_fixture(importers):
    for importer in importers:
        importer.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('proposal', '0013_nullable_last_run'),
    ]

    operations = [
        migrations.RunPython(load_fixture, unload_fixture)
    ]
