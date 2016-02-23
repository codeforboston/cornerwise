# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0026_proposal_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='description',
            field=models.TextField(default=''),
        ),
    ]
