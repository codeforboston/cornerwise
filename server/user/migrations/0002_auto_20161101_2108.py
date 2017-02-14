# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='active',
            field=models.BooleanField(help_text='Users only receive updates for active subscriptions', default=False),
        ),
        migrations.AddField(
            model_name='subscription',
            name='token',
            field=models.CharField(default=user.models.make_token, max_length=64),
        ),
    ]
