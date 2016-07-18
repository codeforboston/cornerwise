# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterUniqueTogether(
            name='project',
            unique_together=set([('name', 'region_name')]),
        ),
    ]
