from __future__ import unicode_literals

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0014_load_fixtures'),
    ]

    operations = [
        migrations.AddField(
            model_name='importer',
            name='run_frequency',
            field=models.DurationField(default=datetime.timedelta(1), help_text='Specifies how often the scraper should run ', validators=[django.core.validators.MinValueValidator(datetime.timedelta(1))]),
        ),
    ]
