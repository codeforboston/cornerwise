from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0019_subscription_activated"),
    ]

    operations = [
        migrations.RemoveField("Subscription", "active"),
        migrations.RenameField("Subscription", "activated", "active"),
    ]
