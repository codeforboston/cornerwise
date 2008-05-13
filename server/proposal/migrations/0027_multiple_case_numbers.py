from django.db import migrations, models

from django.contrib.postgres import fields, indexes, operations


def set_case_numbers(apps, schema_editor):
    Proposal = apps.get_model("proposal", "Proposal")

    for proposal in Proposal.objects.all():
        proposal.case_numbers = [proposal.case_number]
        proposal.save()


class Migration(migrations.Migration):
    dependencies = [
        ("proposal", "0026_event_importer")
    ]

    operations = [
        operations.BtreeGinExtension(),
        migrations.AddField(
            model_name="Proposal",
            name="case_numbers",
            field=fields.ArrayField(
                base_field=models.CharField(max_length=64),
                default=[]
            )),
        migrations.AddIndex(model_name="Proposal",
                            index=indexes.GinIndex(fields=["case_numbers"],
                                                   name="case_numbers_idx")),
        migrations.RunPython(set_case_numbers),
    ]
