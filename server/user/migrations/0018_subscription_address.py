from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0017_usercomment_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='address',
            field=models.CharField(blank=True, help_text='Optional address for the center point', max_length=64),
        ),
    ]
