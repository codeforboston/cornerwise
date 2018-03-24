# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0015_importer_run_frequency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importer',
            name='run_frequency',
            field=models.DurationField(default=datetime.timedelta(1), help_text="Specifies how often the scraper should run. Effectively\n    rounds up to the next day, so values of '3 days' and '2 days, 3 hours' are\n    the same.", validators=[django.core.validators.MinValueValidator(datetime.timedelta(1))]),
        ),
    ]
