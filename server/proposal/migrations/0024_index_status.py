from django.db import migrations, models
import proposal.models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0023_event_agenda_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='status',
            field=models.CharField(db_index=True, max_length=64),
        ),
    ]
