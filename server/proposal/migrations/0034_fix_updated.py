import django.contrib.gis.db.models.fields
from django.db import migrations
from django.contrib.gis.db.models import Max


def fix_updated(apps, _):
    Proposal = apps.get_model("proposal", "Proposal")
    proposals = Proposal.objects.annotate(published=Max("documents__published"))
    for proposal in proposals:
        if proposal.published:
            proposal.updated = proposal.published
            proposal.save()


def do_nothing(apps, _):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('proposal', '0033_non_null_started'),
    ]

    operations = [
        migrations.RunPython(fix_updated, do_nothing),
    ]
