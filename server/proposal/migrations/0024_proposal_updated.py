# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0023_image_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 25, 4, 53, 47, 185790, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
