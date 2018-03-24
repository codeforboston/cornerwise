from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0012_layer_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importer',
            name='last_run',
            field=models.DateTimeField(help_text='Last time the scraper ran', null=True),
        ),
        migrations.AlterField(
            model_name='importer',
            name='region_name',
            field=models.CharField(blank=True, help_text='Default region name, used when\n                                   a proposal in the response JSON does not\n                                   have one set.', max_length=128),
        ),
    ]
