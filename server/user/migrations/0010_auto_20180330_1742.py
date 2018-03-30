import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_auto_20180327_2316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='last_notified',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='updated',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
