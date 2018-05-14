import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0027_multiple_case_numbers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='case_numbers',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), size=None),
        ),
    ]
