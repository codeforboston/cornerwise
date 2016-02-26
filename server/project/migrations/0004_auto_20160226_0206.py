# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_auto_20160216_2012'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='address',
            field=models.CharField(default='', max_length=256),
        ),
        migrations.AddField(
            model_name='project',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='shape',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True),
        ),
    ]
