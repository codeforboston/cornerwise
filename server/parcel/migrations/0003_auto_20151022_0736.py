# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0002_auto_20150913_1811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='parcel',
            field=models.ForeignKey(related_name='attributes', to='parcel.Parcel'),
        ),
    ]
