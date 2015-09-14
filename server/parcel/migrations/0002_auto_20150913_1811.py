# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=256)),
                ('parcel', models.ForeignKey(to='parcel.Parcel')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='attribute',
            unique_together=set([('parcel', 'name')]),
        ),
    ]
