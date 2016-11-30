# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0001_initial'),
        ('proposal', '0003_auto_20160713_2136'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='parcel',
            field=models.ForeignKey(null=True, to='parcel.Parcel'),
        ),
    ]
