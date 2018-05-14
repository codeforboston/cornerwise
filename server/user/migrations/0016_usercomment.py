from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0015_auto_20180510_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ("user", models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)),
                ('subject', models.CharField(max_length=100)),
                ('send_to', models.CharField(max_length=100)),
                ('comment', models.CharField(max_length=1000)),
                ('remote_addr', models.GenericIPAddressField()),
                ('remote_host', models.CharField(max_length=100)),
                ('site_name', models.CharField(max_length=64)),
            ],
        ),
    ]
