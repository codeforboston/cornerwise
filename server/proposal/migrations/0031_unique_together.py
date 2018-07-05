from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0030_event_dept_code'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='event',
            unique_together={('date', 'dept', 'region_name'),
                             ('date', 'title', 'region_name')},
        ),
    ]
