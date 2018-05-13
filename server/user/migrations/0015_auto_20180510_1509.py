import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_userprofile_site_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='radius',
            field=models.FloatField(db_index=True, help_text='Radius in meters', null=True, validators=[django.core.validators.MinValueValidator(50), django.core.validators.MaxValueValidator(10000)]),
        ),
    ]
