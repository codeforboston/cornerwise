from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("parcel", "0003_index_parcel_attrs"),
    ]

    operations = [
        migrations.CreateModel(
            name='LotQuantiles',
            fields=[
                ("town_id", models.IntegerField(primary_key=True, serialize=False)),
                ("small_lot", models.DecimalField(decimal_places=5, max_digits=10)),
                ("medium_lot", models.DecimalField(decimal_places=5, max_digits=10)),
            ],
            options={
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="LotSize",
            fields=[
                ("parcel", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to="parcel.Parcel")),
                ("lot_size", models.DecimalField(db_index=True, decimal_places=5, max_digits=10)),
            ],
            options={
                "managed": False,
            },
        ),
        migrations.AlterField(
            model_name="parcel",
            name="map_no",
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
