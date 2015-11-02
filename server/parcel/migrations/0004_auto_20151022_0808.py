# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0003_auto_20151022_0736'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='parcel',
            options={'managed': True},
        ),
    ]
