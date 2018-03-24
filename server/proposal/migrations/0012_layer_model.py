from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0011_proposal_importer_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='Layer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name shown to users', max_length=100)),
                ('short_name', models.CharField(blank=True, max_length=30)),
                ('description', models.TextField(help_text='A detailed description of the layer')),
                ('icon_text', models.CharField(help_text='Emoji or short string shown as\n                                 shorthand for the layer if there is no icon set.', max_length=10)),
                ('icon', models.FileField(default=None, null=True, upload_to='')),
                ('icon_credit', models.CharField(blank=True, help_text='Many popular icons require that\n                                   proper attribution be given to the original\n                                   author(s). Use this field to provide it.', max_length=100)),
                ('region_name', models.CharField(blank='True', help_text='Used when filtering layers by\n                                   region name', max_length=128)),
                ('url', models.URLField(help_text='URL of the GeoJSON representing the\n                  layer geometry.\n        ')),
                ('envelope', django.contrib.gis.db.models.fields.PolygonField(help_text='Polygon for the bounding envelope\n                                   of the layer geometry. Used to determine\n                                   which layers should be loaded when looking\n                                   at the map. Calculated automatically from\n                                   the geometry in the layer', null=True, srid=4326)),
            ],
        ),
    ]
