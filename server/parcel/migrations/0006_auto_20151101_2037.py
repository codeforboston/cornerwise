# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parcel', '0005_auto_20151022_0808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parcel',
            name='shape_area',
            field=models.DecimalField(decimal_places=24, max_digits=1000, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='parcel',
            name='shape_leng',
            field=models.DecimalField(decimal_places=24, max_digits=1000, blank=True, null=True),
        ),
    ]
