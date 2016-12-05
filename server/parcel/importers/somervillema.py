from django.contrib.gis.gdal import SpatialReference
from django.contrib.gis.utils import LayerMapping
from django.db import IntegrityError
import dbfread
import os

from parcel.models import Parcel

name = "Somerville, MA"

# Note: This is the WKT from M274TaxPar.prj, with one important difference. The
# given WKT specifies Lambert_Conformal_Conic, which is ambiguous. The intended
# meaning is Lambert_Conformal_Conic_2SP.
srs_wkt = 'PROJCS["NAD_1983_StatePlane_Massachusetts_Mainland_FIPS_2001",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["False_Easting",200000.0],PARAMETER["False_Northing",750000.0],PARAMETER["Central_Meridian",-71.5],PARAMETER["Standard_Parallel_1",41.71666666666667],PARAMETER["Standard_Parallel_2",42.68333333333333],PARAMETER["Latitude_Of_Origin",41.0],UNIT["Meter",1.0]]'


def import_shapes(logger):
    srs = SpatialReference(srs_wkt)
    lm = LayerMapping(
        Parcel,
        "/data/shapefiles/M274TaxPar.shp", {
            "shape_leng": "SHAPE_Leng",
            "shape_area": "SHAPE_Area",
            "map_par_id": "MAP_PAR_ID",
            "loc_id": "LOC_ID",
            "poly_type": "POLY_TYPE",
            "map_no": "MAP_NO",
            "source": "SOURCE",
            "plan_id": "PLAN_ID",
            "last_edit": "LAST_EDIT",
            "town_id": "TOWN_ID",
            "shape": "POLYGON"
        },
        source_srs=srs)
    lm.save(strict=True)


def add_assessor_data(logger, file_name="M274Assess.dbf"):
    logger.info("Adding assessor data...")
    # This could be done more efficiently, but it only needs to run once.
    path = os.path.join("/data/shapefiles", file_name)
    dbf = dbfread.DBF(path)
    copy_attributes = [
        "LOT_SIZE", "USE_CODE", "YEAR_BUILT", "BLD_AREA", "UNITS", "STYLE",
        "STORIES", "NUM_ROOMS", "ZONING"
    ]
    for entry in dbf:
        try:
            parcel = Parcel.objects.get(loc_id=entry["LOC_ID"])
            parcel.address_num = entry["ADDR_NUM"]
            parcel.full_street = entry["FULL_STR"]
            parcel.save()
            for attr in copy_attributes:
                if attr in entry:
                    try:
                        parcel.attributes.create(
                            name=attr, value=str(entry[attr]))
                    except IntegrityError:
                        continue
        except Parcel.DoesNotExist:
            continue


def run(logger=None):
    import_shapes(logger)
    add_assessor_data(logger)
