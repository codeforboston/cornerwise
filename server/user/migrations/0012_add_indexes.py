import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_auto_20180331_1640'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='center',
            field=django.contrib.gis.db.models.fields.PointField(geography=True, help_text='Center point of the query. Along with the radius, determines the notification region.', null=True, srid=4326),
        ),
    ]
