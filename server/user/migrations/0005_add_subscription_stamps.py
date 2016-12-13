# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_remove_subscription_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 9, 3, 57, 21, 511024, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscription',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='last_notified',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
