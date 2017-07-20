# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_subscription_require_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='created',
            field=models.DateTimeField(default=datetime.datetime.utcnow),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime.utcnow),
        ),
    ]
