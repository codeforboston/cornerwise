from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_add_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='site_name',
            field=models.CharField(db_index=True, default='somerville.cornerwise.org', help_text='The site where the user created his/her account', max_length=64),
        ),
    ]
