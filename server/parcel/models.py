from django_pgviews import view as pg
from django.contrib.gis.db import models


class ParcelManager(models.GeoManager):
    def containing(self, point):
        return self.filter(shape__contains=point)


class Parcel(models.Model):
    gid = models.AutoField(primary_key=True)
    shape_leng = models.DecimalField(
        max_digits=1000, decimal_places=24, blank=True, null=True)
    shape_area = models.DecimalField(
        max_digits=1000, decimal_places=24, blank=True, null=True)
    map_par_id = models.CharField(max_length=26, blank=True, null=True)
    loc_id = models.CharField(max_length=18, blank=True, null=True, unique=True)
    poly_type = models.CharField(max_length=15, blank=True, null=True)
    map_no = models.CharField(max_length=10, blank=True, null=True)
    source = models.CharField(max_length=15, blank=True, null=True)
    plan_id = models.CharField(max_length=40, blank=True, null=True)
    last_edit = models.IntegerField(blank=True, null=True)
    town_id = models.SmallIntegerField(blank=True, null=True)

    # Not using geometry type here, because the typical use of parcels is to
    # look them up using a 'within' query.
    shape = models.MultiPolygonField(srid=4326, blank=True, null=True)

    # Address:
    address_num = models.CharField(max_length=64, null=True)
    # Stored in all caps:
    full_street = models.CharField(max_length=128, null=True)

    objects = ParcelManager()

    def index_attributes(self):
        return {a.name: a.value for a in self.attributes.all()}


class Attribute(models.Model):
    parcel = models.ForeignKey(Parcel, related_name="attributes")
    name = models.CharField(max_length=64, db_index=True)
    value = models.CharField(max_length=256, db_index=True)

    class Meta:
        unique_together = (("parcel", "name"))



# Views:
class LotQuantiles(pg.View):
    sql = """
    select
        town_id,
        percentile_disc(0.20) within group (order by cast(value as numeric))
                as small_lot,
        percentile_disc(0.80) within group (order by cast(value as numeric))
                as medium_lot
    from parcel_attribute att
    join parcel_parcel p on p.gid = att.parcel_id
    where name='LOT_SIZE'
    group by town_id
    """
    town_id = models.IntegerField(primary_key=True)
    small_lot = models.DecimalField(max_digits=10, decimal_places=5)
    medium_lot = models.DecimalField(max_digits=10, decimal_places=5)

    class Meta:
        managed = False


class LotSize(pg.MaterializedView):
    """
    Since the parcel table does not change often, store this in a materialized
    view. Refresh when new parcels are imported.
    """
    parcel = models.OneToOneField("parcel.Parcel", primary_key=True)
    lot_size = models.DecimalField(max_digits=10, decimal_places=5, db_index=True)

    concurrent_index = "parcel_id"

    sql = """
    select parcel_id, cast(value as numeric) as lot_size from parcel_attribute
    where name='LOT_SIZE'
    """

    class Meta:
        managed = False
