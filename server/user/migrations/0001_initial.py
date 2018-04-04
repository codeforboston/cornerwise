# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import user.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('query', models.BinaryField()),
                ('last_notified', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(related_name='subscriptions', to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('token', models.CharField(max_length=64, default=user.models.make_token)),
                ('nickname', models.CharField(max_length=128, help_text='What do you prefer to be called?')),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
    ]
