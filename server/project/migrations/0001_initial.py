# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0019_auto_20151119_1104'),
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField()),
                ('budget', models.DecimalField(decimal_places=2, max_digits=11)),
                ('funding_source', models.CharField(max_length=64)),
                ('comment', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, unique=True)),
                ('department', models.CharField(max_length=128, db_index=True)),
                ('category', models.CharField(max_length=20, db_index=True)),
                ('approved', models.BooleanField(db_index=True)),
                ('proposals', models.ManyToManyField(to='proposal.Proposal')),
            ],
        ),
        migrations.AddField(
            model_name='budgetitem',
            name='project',
            field=models.ForeignKey(to='project.Project'),
        ),
    ]
