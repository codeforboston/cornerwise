# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0019_auto_20151119_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='skip_cache',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='image',
            name='document',
            field=models.ForeignKey(help_text='Source document for image', null=True, to='proposal.Document'),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.FileField(null=True, upload_to=''),
        ),
    ]
