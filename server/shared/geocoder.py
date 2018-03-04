from django.conf import settings

from scripts import gmaps, arcgis


if settings.GEOCODER == "google":
    Geocoder = gmaps.GoogleGeocoder(settings.GOOGLE_API_KEY)
    Geocoder.bounds = settings.GEO_BOUNDS
elif settings.GEOCODER == "arcgis":
    Geocoder = arcgis.ArcGISCoder(settings.ARCGIS_CLIENT_ID,
                                  settings.ARCGIS_CLIENT_SECRET)
else:
    Geocoder = None
