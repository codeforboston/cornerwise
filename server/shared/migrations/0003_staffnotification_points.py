import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0002_staffnotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffnotification',
            name='points',
            field=django.contrib.gis.db.models.fields.MultiPointField(null=True, srid=4326),
        ),
    ]
