# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0007_image_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='complete',
            field=models.BooleanField(default=False),
        ),
    ]
