# from django.contrib.gis.gdal import SpatialReference
# from django.contrib.gis.utils import LayerMapping
# from django.db import IntegrityError
# import dbfread
import glob
from os import path
import tempfile
from urllib import request
from urllib.parse import urlparse
from zipfile import ZipFile

# from parcel.models import Parcel

name = "Cambridge, MA"

url = "http://gis.cambridgema.gov/download/shp/ASSESSING_ParcelMapIndexFY2016.shp.zip"


def import_shapers(logger):
    (_, zip_path) = tempfile.mkstemp()
    (_, http_message) = request.urlretrieve(url, zip_path)
    zip_file = ZipFile(zip_path)
    ex_dir = tempfile.mkdtemp()
    zip_file.extractall(ex_dir)
    shapefiles = glob.glob1(ex_dir, "*.shp")
    lm = LayerMapping(Parcel, "/data/shapefiles/M274TaxPar.shp", {
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
    })


def run(logger=None):
    pass
