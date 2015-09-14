# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.contrib.gis.db import models

class Parcel(models.Model):
    gid = models.AutoField(primary_key=True)
    shape_leng = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    shape_area = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    map_par_id = models.CharField(max_length=26, blank=True, null=True)
    loc_id = models.CharField(max_length=18, blank=True, null=True)
    poly_type = models.CharField(max_length=15, blank=True, null=True)
    map_no = models.CharField(max_length=4, blank=True, null=True)
    source = models.CharField(max_length=15, blank=True, null=True)
    plan_id = models.CharField(max_length=40, blank=True, null=True)
    last_edit = models.IntegerField(blank=True, null=True)
    bnd_chk = models.CharField(max_length=2, blank=True, null=True)
    no_match = models.CharField(max_length=1, blank=True, null=True)
    town_id = models.SmallIntegerField(blank=True, null=True)
    shape = models.MultiPolygonField(srid=97406, blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'parcel'

class Attribute(models.Model):
    parcel = models.ForeignKey(Parcel)
    name = models.CharField(max_length=64)
    value = models.CharField(max_length=256)

    class Meta:
        unique_together = (("parcel", "name"))
