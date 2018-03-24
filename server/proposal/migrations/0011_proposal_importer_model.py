from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0010_auto_20170709_1127'),
    ]

    operations = [
        migrations.CreateModel(
            name='Importer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Readable name that will be used\n                            to identify the origin of the proposals. ', max_length=128, unique=True)),
                ('region_name', models.CharField(help_text='Default region name, used when\n                                   a proposal in the response JSON does not\n                                   have one set.', max_length=128)),
                ('url', models.URLField(help_text='A URL endpoint that should accept a\n    `when` parameter of the format YYYYmmdd and should respond with a JSON\n    document conforming to the scraper-schema spec.')),
                ('last_run', models.DateTimeField(help_text='Last time the scraper ran')),
            ],
        ),
        migrations.AddField(
            model_name='proposal',
            name='importer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='proposal.Importer'),
        ),
    ]
