from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0023_active_default_null'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercomment',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
