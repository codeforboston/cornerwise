# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('handle', models.CharField(db_index=True, max_length=128)),
                ('published', models.DateTimeField()),
                ('text_value', models.TextField(null=True)),
                ('date_value', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Change',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(max_length=50)),
                ('prop_path', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('url', models.URLField()),
                ('title', models.CharField(help_text='The name of the document', max_length=256)),
                ('field', models.CharField(help_text='The field in which the document was found', max_length=256)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('published', models.DateTimeField(null=True)),
                ('document', models.FileField(upload_to='', null=True)),
                ('fulltext', models.FileField(upload_to='', null=True)),
                ('encoding', models.CharField(default='', max_length=20)),
                ('thumbnail', models.FileField(upload_to='', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(db_index=True, max_length=256)),
                ('date', models.DateTimeField(db_index=True)),
                ('duration', models.DurationField(null=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('image', models.FileField(upload_to='', null=True)),
                ('thumbnail', models.FileField(upload_to='', null=True)),
                ('url', models.URLField(unique=True, null=True)),
                ('skip_cache', models.BooleanField(default=False)),
                ('priority', models.IntegerField(db_index=True, default=0)),
                ('source', models.CharField(default='document', max_length=64)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('document', models.ForeignKey(help_text='Source document for image', to='proposal.Document', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('case_number', models.CharField(help_text='The unique case number assigned by the city', unique=True, max_length=64)),
                ('address', models.CharField(help_text='Street address', max_length=128)),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text='The latitude and longitude', srid=4326)),
                ('region_name', models.CharField(null=True, default='Somerville, MA', max_length=128)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('summary', models.CharField(default='', max_length=1024)),
                ('description', models.TextField(default='')),
                ('source', models.URLField(help_text='The data source for the proposal.', null=True)),
                ('status', models.CharField(max_length=64)),
                ('complete', models.BooleanField(default=False)),
                ('project', models.ForeignKey(to='project.Project', blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='image',
            name='proposal',
            field=models.ForeignKey(related_name='images', to='proposal.Proposal'),
        ),
        migrations.AddField(
            model_name='event',
            name='proposals',
            field=models.ManyToManyField(to='proposal.Proposal', related_name='proposals'),
        ),
        migrations.AddField(
            model_name='document',
            name='event',
            field=models.ForeignKey(help_text='Event associated with this document', to='proposal.Event', null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='proposal',
            field=models.ForeignKey(to='proposal.Proposal'),
        ),
        migrations.AddField(
            model_name='change',
            name='proposal',
            field=models.ForeignKey(related_name='changes', to='proposal.Proposal'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='proposal',
            field=models.ForeignKey(related_name='attributes', to='proposal.Proposal'),
        ),
        migrations.AlterUniqueTogether(
            name='image',
            unique_together=set([('proposal', 'image')]),
        ),
        migrations.AlterUniqueTogether(
            name='document',
            unique_together=set([('proposal', 'url')]),
        ),
    ]
