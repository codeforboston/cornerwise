from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0022_null_last_notified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='active',
            field=models.DateTimeField(help_text='If the subscription is active, the datetime when it was last activated', null=True),
        ),
    ]
