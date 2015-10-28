# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from utils import normalize

def add_handle(apps, schema_editor):
    Attribute = apps.get_model("proposal", "Attribute")
    db_alias = schema_editor.connection.alias
    atts = Attribute.objects.using(db_alias).all()

    for att in atts:
        att.handle = normalize(att.name)
        att.save()

def clear_handle(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0013_attribute_handle'),
    ]

    operations = [
        migrations.RunPython(add_handle, clear_handle),
        migrations.AlterField(
            model_name='attribute',
            name='handle',
            field=models.CharField(max_length=128),
        ),
    ]
