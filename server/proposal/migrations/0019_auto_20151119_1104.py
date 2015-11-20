# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0018_auto_20151101_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='proposals',
            field=models.ManyToManyField(related_name='proposals', to='proposal.Proposal'),
        ),
        migrations.AlterField(
            model_name='image',
            name='proposal',
            field=models.ForeignKey(to='proposal.Proposal', related_name='images'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='summary',
            field=models.CharField(max_length=256, default=''),
        ),
    ]
