# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_remove_project_proposals'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='description',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='project',
            name='justification',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='project',
            name='region_name',
            field=models.CharField(max_length=128, default='Somerville, MA'),
        ),
        migrations.AddField(
            model_name='project',
            name='website',
            field=models.URLField(null=True),
        ),
    ]
