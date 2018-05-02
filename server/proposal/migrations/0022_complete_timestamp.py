from django.db import migrations, models


def set_completion_date(apps, schema_editor):
    Attribute = apps.get_model("proposal", "Attribute")

    for attribute in Attribute.objects.filter(handle="decision"):
        p = attribute.proposal
        p.complete_date = attribute.published
        p.save()


def backwards(apps, schema_editor):
    Proposal = apps.get_model("proposal", "Proposal")

    Proposal.objects.filter(complete_date__isnull=False)\
                    .update(complete=True)


class Migration(migrations.Migration):
    dependencies = [
        ("proposal", "0021_fix_on_delete")
    ]

    operations = [
        migrations.AddField(
            model_name="Proposal",
            name="complete_date",
            field=models.DateTimeField(null=True)),
        migrations.RunPython(set_completion_date, backwards),
        migrations.RemoveField("Proposal", "complete"),
        migrations.RenameField("Proposal", "complete_date", "complete")
    ]
