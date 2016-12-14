# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_add_subscription_stamps'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='created',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
