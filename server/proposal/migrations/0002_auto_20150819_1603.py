# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('url', models.URLField()),
                ('title', models.CharField(max_length=256, help_text='The name of the document')),
                ('field', models.CharField(max_length=256, help_text='The field in which the document was found')),
                ('document', models.FileField(null=True, upload_to='')),
            ],
        ),
        migrations.RenameModel(
            old_name='ProposalEvent',
            new_name='Event',
        ),
        migrations.RemoveField(
            model_name='proposaldocument',
            name='event',
        ),
        migrations.RemoveField(
            model_name='proposaldocument',
            name='proposal',
        ),
        migrations.AlterField(
            model_name='proposal',
            name='region_name',
            field=models.CharField(max_length=128, null=True, default='Somerville, MA'),
        ),
        migrations.DeleteModel(
            name='ProposalDocument',
        ),
        migrations.AddField(
            model_name='document',
            name='event',
            field=models.ForeignKey(null=True, to='proposal.Event', help_text='Event associated with this document'),
        ),
        migrations.AddField(
            model_name='document',
            name='proposal',
            field=models.ForeignKey(to='proposal.Proposal'),
        ),
        migrations.AlterUniqueTogether(
            name='document',
            unique_together=set([('proposal', 'url')]),
        ),
    ]
