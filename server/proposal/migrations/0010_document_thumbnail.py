# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0009_document_fulltext'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='thumbnail',
            field=models.FileField(null=True, upload_to=''),
        ),
    ]
