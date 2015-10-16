# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0012_auto_20150922_2054'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='handle',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
