from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0025_auto_20180506_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='importer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='proposal.Importer'),
        ),
    ]
