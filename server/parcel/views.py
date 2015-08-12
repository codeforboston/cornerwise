from django.contrib.gis.geos import Point
from django.shortcuts import render
import json

from shared.geo import geojson_data
from shared.request import make_response, ErrorResponse

from .models import Parcel

def parcels_for_request(req):
    """
    Helper function for retrieving the parcel(s) at a given latitude and
    longitude.
    """
    try:
        lng = float(req.GET["long"])
        lat = float(req.GET["lat"])
    except KeyError as kerr:
        raise ErrorResponse(
            "Bad parameters",
            {"error": "Missing required key: {}".format(str(kerr))})
    except ValueError:
        raise ErrorResponse(
            "Bad parameter",
            {"error": "Bad value for latitude and longitude."})

    return Parcel.objects.\
        filter(shape__contains=Point(lng, lat, srid=4326)).\
        transform()

def make_parcel_data(parcel):
    return {
        "shape": geojson_data(parcel.shape),
        "properties": {
            "type": parcel.poly_type,
        }
    }

@make_response()
def parcels_at_point(req):
    parcels = parcels_for_request(req)
    return {
        "parcels": [make_parcel_data(parcel) for parcel in parcels]
    }
