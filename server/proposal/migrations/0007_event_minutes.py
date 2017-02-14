# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proposal", "0006_auto_20170111_2217"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="minutes",
            field=models.URLField(blank=True),
        ),
    ]
