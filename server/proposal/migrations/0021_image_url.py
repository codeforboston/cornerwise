# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0020_remote_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='url',
            field=models.URLField(unique=True, null=True),
        ),
    ]
