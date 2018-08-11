import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0035_set_summary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(geography=True, help_text='The latitude and longitude', null=True, srid=4326),
        ),
    ]
