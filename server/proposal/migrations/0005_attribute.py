# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0004_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('string_value', models.CharField(null=True, max_length=256)),
                ('text_value', models.TextField(null=True)),
                ('date_value', models.DateTimeField(null=True)),
                ('proposal', models.ForeignKey(to='proposal.Proposal', related_name='attributes')),
            ],
        ),
    ]
