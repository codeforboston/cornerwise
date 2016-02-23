# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0027_auto_20160221_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='summary',
            field=models.CharField(max_length=1024, default=''),
        ),
    ]
