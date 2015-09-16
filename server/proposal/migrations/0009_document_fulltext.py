# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0008_proposal_complete'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='fulltext',
            field=models.FileField(upload_to='', null=True),
        ),
    ]
