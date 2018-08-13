from django.db import migrations
import proposal.models

def set_processing_status(apps, _):
    Document = apps.get_model("proposal", "Document")
    Document.objects.filter(document__isnull=False, fulltext__isnull=False,
                            thumbnail__isnull=False)\
                    .update(processing_state="processed")


def clear_processing_status(apps, _):
    Document = apps.get_model("proposal", "Document")
    Document.objects.update(processing_state=0)


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0037_status_from_recommendation'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='processing_state',
            field=proposal.models.ProcessingStateField(choices=[('not_processed', 0), ('failed', 1), ('skip', 9), ('processed', 10)], default=0, db_index=True),
        ),
        migrations.RunPython(set_processing_status, clear_processing_status)
    ]
