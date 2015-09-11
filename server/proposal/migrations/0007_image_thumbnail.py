# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0006_image_proposal'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='thumbnail',
            field=models.FileField(upload_to='', null=True),
        ),
    ]
