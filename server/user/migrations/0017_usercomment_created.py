from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0016_usercomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercomment',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
