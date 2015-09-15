# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0003_document_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('image', models.FileField(upload_to='')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('document', models.ForeignKey(to='proposal.Document')),
            ],
        ),
    ]
