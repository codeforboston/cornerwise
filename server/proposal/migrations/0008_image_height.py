from __future__ import unicode_literals

import io

import django.db.models.deletion
import PIL
from urllib import request
from django.db import migrations, models


def forwards(apps, schema_editor):
    Image = apps.get_model("proposal", "Image")
    db_alias = schema_editor.connection.alias

    images = Image.objects.all()
    for image in images:
        if image.image:
            pil_image = PIL.Image.open(image.image)
        elif image.url:
            with request.urlopen(image.url) as u:
                pil_image = PIL.Image.open(io.BytesIO(u.read()))
        else:
            continue

        image.width = pil_image.width
        image.height = pil_image.height
        pil_image.close()
        image.save()


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("proposal", "0007_event_minutes"),
    ]

    operations = [
        migrations.AddField(
            model_name="image",
            name="height",
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="image",
            name="width",
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
        migrations.RunPython(forwards, backwards)
    ]
