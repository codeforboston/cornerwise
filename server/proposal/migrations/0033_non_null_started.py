from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):
    dependencies = [
        ('proposal', "0032_proposal_started"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proposal",
            name="started",
            field=models.DateTimeField(default=timezone.now, null=False, help_text="When the proposal was first seen, or the date of the first public hearing; whichever is first", db_index=True),
            preserve_default=False,
        ),
    ]
