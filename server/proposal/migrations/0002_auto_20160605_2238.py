# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Changeset',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('change_blob', models.BinaryField()),
                ('proposal', models.ForeignKey(related_name='changes', to='proposal.Proposal', on_delete=models.CASCADE)),
            ],
        ),
        migrations.RemoveField(
            model_name='change',
            name='proposal',
        ),
        migrations.DeleteModel(
            name='Change',
        ),
    ]
