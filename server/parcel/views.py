from django.contrib.gis.geos import Point
from django.db.models import Q
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
        lng = float(req.GET["lng"])
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

def parcels_for_multi_request(req):
    #
    # [{ "lat": <lat>,
    #    "lng": <lng>,
    #    "id": <id> }]
    try:
        print(req.GET["points"])
        points = json.loads(req.GET["points"])
    except KeyError as kerr:
        raise ErrorResponse(
            "",
            {"error": "Missing required key: {}".format(kerr)})
    except ValueError:
        raise ErrorResponse(
            "",
            {"error": "Malformed 'points' value; must be valid JSON array: {}".format(e)})

    query = None
    for point in points:
        q = Q(shape__contains=Point(point["lng"], point["lat"], srid=4326))
        if query:
            query |= q
        else:
            query = qe

    return Parcel.objects.filter(query)

def make_parcel_data(parcel, include_attributes=False):
    d = geojson_data(parcel.shape)
    d["properties"] = {
        "type": parcel.poly_type,
        "loc_id": parcel.loc_id
    }

    if include_attributes:
        d["properties"].update(
            {a.name: a.value for a in parcel.attribute_set.all()})

    return d

@make_response()
def parcels_at_point(req):
    parcels = parcels_for_request(req)
    return {
        "parcels": [make_parcel_data(parcel) for parcel in parcels]
    }

@make_response()
def parcel_at_point(req):
    try:
        parcel = parcels_for_request(req)[0]
    except IndexError:
        raise ErrorResponse(
            "No matching parcels found",
            status=404)
    return make_parcel_data(parcel)

@make_response()
def parcel_with_loc_id(req, loc_id=None):
    if not loc_id:
        loc_id = req.GET["loc_id"]

    parcel = Parcel.objects.get(loc_id=loc_id)
    return make_parcel_data(parcel, include_attributes=True)


@make_response()
def parcels_at_points(req):
    parcels = parcels_for_multi_request(req)
    return {
        "parcels": [make_parcel_data(parcel) for parcel in parcels]
    }
