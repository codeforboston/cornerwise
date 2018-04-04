import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_auto_20180330_1742'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='center',
            field=django.contrib.gis.db.models.fields.PointField(geography=True, help_text='Center point of the query. Along with the radius, determines the notification region.', null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='radius',
            field=models.FloatField(db_index=True, help_text='Radius in meters', null=True, validators=[django.core.validators.MinValueValidator(50), django.core.validators.MaxValueValidator(300)]),
        ),
    ]
