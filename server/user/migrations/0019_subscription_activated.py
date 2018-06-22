from django.db import migrations, models
import django.utils.timezone


def set_activated_date(apps, schema_editor):
    Subscription = apps.get_model("user", "Subscription")

    for sub in Subscription.objects.filter(active=True):
        sub.activated = sub.created
        sub.save()


def backwards(apps, schema_editor):
    Subscription = apps.get_model("user", "Subscription")

    Subscription.objects.filter(activated__isnull=False)\
                        .update(active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0018_subscription_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='activated',
            field=models.DateTimeField(default=django.utils.timezone.now,
                                       null=True),
        ),
        migrations.RunPython(set_activated_date, backwards),
    ]
