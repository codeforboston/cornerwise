# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0022_image_priority'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='source',
            field=models.CharField(max_length=64, default='document'),
        ),
    ]
