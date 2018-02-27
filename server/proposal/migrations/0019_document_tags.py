# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proposal", "0018_importer_timezone"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="tags",
            field=models.CharField(blank=True, help_text="comma-separated list of tags", max_length=256),
        ),
    ]
