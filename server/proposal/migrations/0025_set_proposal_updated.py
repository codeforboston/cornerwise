from django.db import models, migrations

def set_updated(apps, schema_editor):
    Proposal = apps.get_model("proposal", "Proposal")
    db_alias = schema_editor.connection.alias
    proposals = Proposal.objects.using(db_alias).all()

    for prop in proposals:
        prop.updated = prop.modified
        prop.save()

def noop(_, __):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ("proposal", "0024_proposal_updated")
    ]

    operations = [
        migrations.RunPython(set_updated, noop)
    ]
