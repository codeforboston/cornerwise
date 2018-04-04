from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Actions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('send_notifications', 'Can send notifications to users'),
                                ("view_debug_logs", "Can view celery debugging logs"),),
                'managed': False,
            },
        ),
    ]
