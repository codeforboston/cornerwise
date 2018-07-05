from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0021_auto_20180704_2342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='last_notified',
            field=models.DateTimeField(null=True),
        ),
    ]
