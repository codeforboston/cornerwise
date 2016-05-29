# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Parcel',
            fields=[
                ('gid', models.AutoField(primary_key=True, serialize=False)),
                ('shape_leng', models.DecimalField(null=True, decimal_places=24, max_digits=1000, blank=True)),
                ('shape_area', models.DecimalField(null=True, decimal_places=24, max_digits=1000, blank=True)),
                ('map_par_id', models.CharField(null=True, max_length=26, blank=True)),
                ('loc_id', models.CharField(null=True, max_length=18, blank=True)),
                ('poly_type', models.CharField(null=True, max_length=15, blank=True)),
                ('map_no', models.CharField(null=True, max_length=4, blank=True)),
                ('source', models.CharField(null=True, max_length=15, blank=True)),
                ('plan_id', models.CharField(null=True, max_length=40, blank=True)),
                ('last_edit', models.IntegerField(null=True, blank=True)),
                ('town_id', models.SmallIntegerField(null=True, blank=True)),
                ('shape', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True, blank=True)),
                ('address_num', models.CharField(null=True, max_length=64)),
                ('full_street', models.CharField(null=True, max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='attribute',
            name='parcel',
            field=models.ForeignKey(to='parcel.Parcel', related_name='attributes'),
        ),
        migrations.AlterUniqueTogether(
            name='attribute',
            unique_together=set([('parcel', 'name')]),
        ),
    ]
