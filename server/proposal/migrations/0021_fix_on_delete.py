from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0020_auto_20180331_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='event',
            field=models.ForeignKey(help_text='Event associated with this document', null=True, on_delete=django.db.models.deletion.SET_NULL, to='proposal.Event'),
        ),
        migrations.AlterField(
            model_name='image',
            name='document',
            field=models.ForeignKey(help_text='Source document for image', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='images', to='proposal.Document'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.Project'),
        ),
    ]
