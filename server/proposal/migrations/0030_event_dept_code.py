from django.db import migrations, models, utils

import re


def set_dept_code(apps, schema_editor):
    Event = apps.get_model("proposal", "Event")
    for event in Event.objects.all():
        if "Zoning Board" in event.title:
            event.dept = "zba"
        elif "Planning Board" in event.title:
            event.dept = "pb"
        else:
            continue

        if Event.objects.filter(date=event.date,
                                dept=event.dept,
                                region_name=event.region_name).exists():
            for p in event.proposals:
                existing.proposals.add(p)
            existing.agenda_url = existing.agenda_url or event.agenda_url
            existing.minutes = existing.minutes or event.minutes
            event.delete()


def do_nothing(_, __):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0029_attribute_admin_properties'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='dept',
            field=models.CharField(null=True, help_text='Department code, used to ensure event uniqueness', max_length=20),
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together={('date', 'dept', 'region_name')},
        ),

        migrations.RunPython(set_dept_code, do_nothing)
    ]
