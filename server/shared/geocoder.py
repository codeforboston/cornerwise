from django.conf import settings

from django.contrib.gis.geos import Point

from scripts import gmaps, arcgis


if settings.GEOCODER == "google":
    Geocoder = gmaps.GoogleGeocoder(settings.GOOGLE_API_KEY)
    Geocoder.bounds = settings.GEO_BOUNDS
elif settings.GEOCODER == "arcgis":
    Geocoder = arcgis.ArcGISCoder(settings.ARCGIS_CLIENT_ID,
                                  settings.ARCGIS_CLIENT_SECRET)
else:
    Geocoder = None


def as_point(geo_response):
    return Point(x=geo_response["location"]["lng"],
                 y=geo_response["location"]["lat"],
                 srid=4326)


def geocode_tuples(addrs, **kwargs):
    return [(addr, as_point(gr), gr["formatted_name"]) if gr else addr
            for addr, gr in
            zip(addrs, Geocoder.geocode(addrs, **kwargs))]
