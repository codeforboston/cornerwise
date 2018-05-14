from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shared', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('addresses', models.TextField(blank=True, default='')),
                ('proposals', models.TextField(blank=True, default='')),
                ('radius', models.FloatField()),
                ('message', models.TextField()),
                ('subscribers', models.IntegerField()),
                ('region', models.CharField(max_length=64)),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
