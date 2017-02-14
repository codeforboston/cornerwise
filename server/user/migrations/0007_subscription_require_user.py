# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def forwards(apps, schema_editor):
    Subscription = apps.get_model("user", "Subscription")
    db_alias = schema_editor.connection.alias
    Subscription.objects.using(db_alias).filter(user=None).delete()


def backwards(apps, schema_editor):
    # Nothing to do
    pass


class Migration(migrations.Migration):

    dependencies = [("user", "0006_subscription_default_created"), ]

    operations = [
        migrations.RunPython(forwards, backwards),
        migrations.AddField(
            model_name="subscription",
            name="include_events",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Include events for a specified region",
                max_length=256), ),
        migrations.AlterField(
            model_name="subscription",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subscriptions",
                to=settings.AUTH_USER_MODEL), ),
    ]
