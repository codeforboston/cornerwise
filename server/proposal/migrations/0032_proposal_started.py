from django.db import migrations, models
from django.utils import timezone


def set_started(apps, _):
    Proposal = apps.get_model("proposal", "Proposal")
    for proposal in Proposal.objects.all():
        started = min(proposal.created, proposal.updated)
        try:
            first_hearing_date = proposal.events.order_by("date")\
                                                .values_list("date", flat=True)[0]
            started = min(started, first_hearing_date)
        except IndexError:
            pass
        proposal.started = started
        proposal.save()


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0031_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='started',
            field=models.DateTimeField(default=timezone.now, null=True, help_text="When the proposal was first seen, or the date of the first public hearing; whichever is first", db_index=True),
            preserve_default=False,
        ),

        migrations.RunPython(set_started),
    ]
