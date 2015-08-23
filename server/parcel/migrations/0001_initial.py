# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Parcel',
            fields=[
                ('gid', models.AutoField(serialize=False, primary_key=True)),
                ('shape_leng', models.DecimalField(null=True, decimal_places=65535, blank=True, max_digits=65535)),
                ('shape_area', models.DecimalField(null=True, decimal_places=65535, blank=True, max_digits=65535)),
                ('map_par_id', models.CharField(null=True, blank=True, max_length=26)),
                ('loc_id', models.CharField(null=True, blank=True, max_length=18)),
                ('poly_type', models.CharField(null=True, blank=True, max_length=15)),
                ('map_no', models.CharField(null=True, blank=True, max_length=4)),
                ('source', models.CharField(null=True, blank=True, max_length=15)),
                ('plan_id', models.CharField(null=True, blank=True, max_length=40)),
                ('last_edit', models.IntegerField(null=True, blank=True)),
                ('bnd_chk', models.CharField(null=True, blank=True, max_length=2)),
                ('no_match', models.CharField(null=True, blank=True, max_length=1)),
                ('town_id', models.SmallIntegerField(null=True, blank=True)),
                ('shape', django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=97406, blank=True)),
            ],
            options={
                'db_table': 'parcel',
                'managed': False,
            },
        ),
    ]
