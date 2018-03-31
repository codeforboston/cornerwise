import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0019_document_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(geography=True, help_text='The latitude and longitude', srid=4326),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='region_name',
            field=models.CharField(db_index=True, default='Somerville, MA', max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='updated',
            field=models.DateTimeField(db_index=True),
        ),
    ]
