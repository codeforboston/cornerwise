from django.db import migrations, models
import django.utils.timezone
import proposal.models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0024_index_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changeset',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='document',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='event',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='image',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='image',
            name='thumbnail',
            field=models.FileField(null=True, upload_to=proposal.models.upload_image_to),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
