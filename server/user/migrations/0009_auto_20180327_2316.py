# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models

from utils import bounds_from_box


def forwards(apps, schema_editor):
    Subscription = apps.get_model("user", "Subscription")
    db_alias = schema_editor.connection.alias
    for sub in Subscription.objects.using(db_alias).all():
        query = sub.query_dict
        if "box" in query:
            sub.box = bounds_from_box(query["box"])
            sub.save()


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_auto_20170404_2015'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='box',
            field=django.contrib.gis.db.models.fields.PolygonField(db_index=True, help_text='The notification region. Either this or the center and radius should be set.', null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='subscription',
            name='center',
            field=django.contrib.gis.db.models.fields.PointField(db_index=True, help_text='Center point of the query. Along with the radius, determines the notification region.', null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='subscription',
            name='radius',
            field=models.FloatField(db_index=True, help_text='Radius in meters', null=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='region_name',
            field=models.CharField(db_index=True, help_text='Only subscribe to updates in this region', max_length=128, null=True),
        ),
    ]
