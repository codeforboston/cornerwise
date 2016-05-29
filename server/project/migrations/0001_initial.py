# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('year', models.IntegerField()),
                ('budget', models.DecimalField(max_digits=11, decimal_places=2)),
                ('funding_source', models.CharField(max_length=64)),
                ('comment', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('department', models.CharField(db_index=True, max_length=128)),
                ('category', models.CharField(db_index=True, max_length=20)),
                ('region_name', models.CharField(default='Somerville, MA', max_length=128)),
                ('shape', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True)),
                ('description', models.TextField(default='')),
                ('justification', models.TextField(default='')),
                ('website', models.URLField(null=True)),
                ('approved', models.BooleanField(db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='budgetitem',
            name='project',
            field=models.ForeignKey(to='project.Project'),
        ),
    ]
