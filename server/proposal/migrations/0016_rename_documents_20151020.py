from django.db import models, migrations

import os, re
from urllib.parse import urlparse
from proposal.cleanup import rename_document

def standardize_name(apps, schema_editor):
    Document = apps.get_model("proposal", "Document")
    db_alias = schema_editor.connection.alias
    docs = Document.objects.using(db_alias).all()

    for doc in docs:
        rename_document(doc)

def revert_names(apps, schema_editor):
    Document = apps.get_model("proposal", "Document")
    db_alias = schema_editor.connection.alias
    docs = Document.objects.using(db_alias).all()

    for doc in docs:
        if doc.url:
            pieces = urlparse(doc.url)
            old_name = os.path.basename(pieces.path)

class Migration(migrations.Migration):
    dependencies = [
        ('proposal', '0015_auto_20151018_0235')
    ]

    operations = [
        migrations.RunPython(standardize_name, revert_names)
    ]
