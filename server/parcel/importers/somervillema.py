from django.contrib.gis.gdal import SpatialReference
from django.contrib.gis.utils import LayerMapping
from django.db import IntegrityError
import dbfread
import os
import shutil

import glob
import tempfile
from urllib import request
from urllib.parse import urlparse
from zipfile import ZipFile

from parcel.models import Parcel

name = "Somerville, MA"
shapefile_url = "http://wsgw.mass.gov/data/gispub/shape/l3parcels/L3_SHP_M274_SOMERVILLE.zip"

# Note: This is the WKT from M274TaxPar.prj, with one important difference. The
# given WKT specifies Lambert_Conformal_Conic, which is ambiguous. The intended
# meaning is Lambert_Conformal_Conic_2SP.
srs_wkt = 'PROJCS["NAD_1983_StatePlane_Massachusetts_Mainland_FIPS_2001",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["False_Easting",200000.0],PARAMETER["False_Northing",750000.0],PARAMETER["Central_Meridian",-71.5],PARAMETER["Standard_Parallel_1",41.71666666666667],PARAMETER["Standard_Parallel_2",42.68333333333333],PARAMETER["Latitude_Of_Origin",41.0],UNIT["Meter",1.0]]'


def import_shapes(shapefile_path, logger):
    srs = SpatialReference(srs_wkt)
    lm = LayerMapping(
        Parcel,
        shapefile_path, {
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


def download_shapefiles(url, logger):
    if logger:
        logger.info("Downloading Somerville shapefiles...")
    (_, zip_path) = tempfile.mkstemp()
    (_, http_message) = request.urlretrieve(url, zip_path)
    if logger:
        logger.info("Download complete.")

    zip_dir = tempfile.mkdtemp()
    ZipFile(zip_path).extractall(zip_dir)
    os.unlink(zip_path)

    return os.path.join(zip_dir, os.listdir(zip_dir)[0])


def add_assessor_data(assessor_data_file, logger):
    if logger:
        logger.info("Adding assessor data...")
    # This could be done more efficiently, but it only needs to run once.
    dbf = dbfread.DBF(assessor_data_file)
    copy_attributes = [
        "LOT_SIZE", "USE_CODE", "YEAR_BUILT", "BLD_AREA", "UNITS", "STYLE",
        "STORIES", "NUM_ROOMS", "ZONING"
    ]
    processed_ids = set()
    for entry in dbf:
        loc_id = entry["LOC_ID"]
        if loc_id in processed_ids:
            continue
        processed_ids.add(loc_id)

        try:
            parcel = Parcel.objects.get(loc_id=loc_id)
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
    shapefiles_dir = download_shapefiles(shapefile_url, logger)

    try:
        shapefile = os.path.join(
            shapefiles_dir, glob.glob1(shapefiles_dir, "M274TaxPar.shp")[0])
        assessor_data = os.path.join(
            shapefiles_dir, glob.glob1(shapefiles_dir, "M274Assess.dbf")[0])
        import_shapes(shapefile, logger)
        add_assessor_data(assessor_data, logger)
    finally:
        shutil.rmtree(shapefiles_dir)
