# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from datetime import datetime

import pytz

default_created = pytz.timezone("US/Eastern").localize(datetime(2016, 1, 1))


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0004_proposal_parcel'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime(2016, 1, 1)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.CharField(max_length=256, default='Somerville City Hall, 93 Highland Ave'),
        ),
        migrations.AddField(
            model_name='event',
            name='region_name',
            field=models.CharField(max_length=128, default='Somerville, MA'),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('date', 'title', 'region_name')]),
        ),
    ]
