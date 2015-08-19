# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0002_auto_20150819_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 8, 1, 0, 0)),
            preserve_default=False,
        ),
    ]
