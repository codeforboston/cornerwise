# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0010_document_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='encoding',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
    ]
