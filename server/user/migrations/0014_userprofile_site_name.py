from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_subscription_site_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='site_name',
            field=models.CharField(db_index=True, default='somerville.cornerwise.org', help_text='The site where the user created his/her account', max_length=64),
        ),
    ]
