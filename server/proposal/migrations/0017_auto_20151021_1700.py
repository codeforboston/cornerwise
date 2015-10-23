# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0016_rename_documents_20151020'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attribute',
            name='string_value',
        ),
        migrations.RemoveField(
            model_name='event',
            name='proposal',
        ),
        migrations.AddField(
            model_name='event',
            name='proposals',
            field=models.ManyToManyField(to='proposal.Proposal'),
        ),
    ]
