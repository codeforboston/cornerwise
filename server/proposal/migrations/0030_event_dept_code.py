from django.db import migrations, models
Q = models.Q

def set_dept_code(apps, schema_editor):
    Event = apps.get_model("proposal", "Event")
    for event in Event.objects.all():
        if "Zoning Board" in event.title:
            event.dept = "zba"
        elif "Planning Board" in event.title:
            event.dept = "pb"
        else:
            continue

        others = Event.objects.filter(Q(pk__gt=event.pk, date=event.date,
                                        region_name=event.region_name) &
                                      (Q(dept=event.dept) |
                                       Q(title=event.title)))
        if others.exists():
            for other in others:
                for p in event.proposals:
                    other.proposals.add(p)
                event.agenda_url = event.agenda_url or other.agenda_url
                event.minutes = event.minutes or other.minutes
            others.delete()


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

        migrations.RunPython(set_dept_code, do_nothing)
    ]
