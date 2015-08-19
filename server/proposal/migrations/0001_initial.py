# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('case_number', models.CharField(unique=True, help_text='The unique case number assigned by the city', max_length=64)),
                ('address', models.CharField(help_text='Street address', max_length=128)),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text='The latitude and longitude', srid=4326)),
                ('region_name', models.CharField(null=True, max_length=128)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('summary', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('source', models.URLField(help_text='The data source for the proposal.', null=True)),
                ('status', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='ProposalDocument',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('url', models.URLField()),
                ('document', models.FileField(upload_to='', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProposalEvent',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('date', models.DateTimeField()),
                ('duration', models.DurationField(null=True)),
                ('description', models.TextField()),
                ('proposal', models.ForeignKey(to='proposal.Proposal')),
            ],
        ),
        migrations.AddField(
            model_name='proposaldocument',
            name='event',
            field=models.ForeignKey(to='proposal.ProposalEvent', null=True),
        ),
        migrations.AddField(
            model_name='proposaldocument',
            name='proposal',
            field=models.ForeignKey(to='proposal.Proposal'),
        ),
    ]
