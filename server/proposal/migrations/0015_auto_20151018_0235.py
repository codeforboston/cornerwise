# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0014_auto_20151016_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='published',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 17, 0, 0)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='attribute',
            name='handle',
            field=models.CharField(db_index=True, max_length=128),
        ),
    ]
