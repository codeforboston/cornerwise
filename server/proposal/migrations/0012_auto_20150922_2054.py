# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0011_document_encoding'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='published',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='encoding',
            field=models.CharField(default='', max_length=20),
        ),
    ]
