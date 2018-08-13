import django.contrib.gis.db.models.fields
from django.db import migrations, models

import re


def set_approval_status(apps, _):
    Attribute = apps.get_model("proposal", "Attribute")
    Proposal = apps.get_model("proposal", "Proposal")
    recommend_attrs = Attribute.objects.filter(handle="recommendation",
                                proposal__complete=None,
                                proposal__region_name="Somerville, MA")
    Proposal.objects.filter(
        attributes__in=recommend_attrs.filter(
            models.Q(text_value__istartswith="conditional approval") |
            models.Q(text_value__istartswith="approval")))\
                     .update(status="Recommend Approval")
    Proposal.objects.filter(
        attributes__in=recommend_attrs.filter(text_value__istartswith="denial",))\
                     .update(status="Recommend Denial")


def clear_approval_status(apps, _):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("proposal", "0036_nullable_location"),
    ]

    operations = [
        migrations.RunPython(set_approval_status, clear_approval_status),
    ]
