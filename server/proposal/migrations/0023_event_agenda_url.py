from django.db import migrations, models
import proposal.models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0022_complete_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='agenda_url',
            field=models.URLField(blank=True),
        ),
    ]
