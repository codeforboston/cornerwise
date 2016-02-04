# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_remove_project_proposals'),
        ('proposal', '0025_set_proposal_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='project',
            field=models.ForeignKey(to='project.Project', blank=True, null=True),
        ),
    ]
