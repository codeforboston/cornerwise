# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0004_auto_20151022_0808'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcel',
            name='address_num',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='parcel',
            name='full_street',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
