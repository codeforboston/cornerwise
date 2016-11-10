# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_userprofile_language'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='token',
        ),
    ]
