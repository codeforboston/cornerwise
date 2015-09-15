# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0005_attribute'),
    ]

    operations = [
        migrations.DeleteModel("Image"),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('image', models.FileField(upload_to='')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('document', models.ForeignKey(to='proposal.Document', null=True)),
                ('proposal', models.ForeignKey(to='proposal.Proposal')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='image',
            unique_together=set([('proposal', 'image')]),
        ),
    ]
