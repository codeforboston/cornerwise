# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_auto_20160226_0206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='address',
        ),
        migrations.RemoveField(
            model_name='project',
            name='location',
        ),
    ]
