from django.db import models, migrations

def add_address(apps, schema_editor):
    Parcel = apps.get_model("parcel", "Parcel")

    db_alias = schema_editor.connection.alias

    for parcel in Parcel.objects.all():
        attrs = parcel.attributes.filter(name__in=["FULL_STR", "ADDR_NUM"])
        for attr in attrs:
            if attr.name == "FULL_STR":
                parcel.full_street = attr.value
            elif attr.name == "ADDR_NUM":
                parcel.address_num = attr.value
        try:
            parcel.save()
        except Exception as _:
            continue


def do_nothing(_, __): pass


class Migration(migrations.Migration):
    dependencies = [
        ('parcel', '0006_auto_20151101_2037')
    ]

    operations = [
        migrations.RunPython(add_address, do_nothing)
    ]
