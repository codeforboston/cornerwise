# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0021_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='priority',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
