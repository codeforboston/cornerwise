import django.contrib.gis.db.models.fields
from django.db import migrations, models


def fix_summary(apps, _):
    Attribute = apps.get_model("proposal", "Attribute")
    attributes = Attribute.objects.filter(handle="legal_notice",
                                          proposal__summary="")
    for attr in attributes:
        prop = attr.proposal
        if not prop.summary.strip():
            prop.summary = attr.text_value
            prop.save()


def clear_summary(apps, _):
    Proposal = apps.get_model("proposal", "Proposal")
    Proposal.objects.all().update(summary="")


class Migration(migrations.Migration):
    dependencies = [
        ("proposal", "0034_fix_updated"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proposal",
            name="summary",
            field=models.TextField(blank=True, default="")
        ),
        migrations.RunPython(fix_summary, clear_summary),
    ]
