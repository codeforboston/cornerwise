from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0028_auto_20180513_0707'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='hidden',
            field=models.BooleanField(default=False, help_text='Admin setting: prevents an attribute from appearing in proposal detail views'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='ignore_updates',
            field=models.BooleanField(default=False, help_text='Admin setting: only allow manual updates to this attribute. Values scraped from documents or from importers will be ignored.'),
        ),
    ]
