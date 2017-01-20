from django.conf.settings import FOURSQUARE_CLIENT, FOURSQUARE_SECRET

from collections import namedtuple
from datetime import datetime
from urllib import error, parse, request
import json

from shared.address import same_address


def venue_search(lat,
                 lng,
                 address,
                 client_id=FOURSQUARE_CLIENT,
                 client_secret=FOURSQUARE_SECRET):
    url = "https://api.foursquare.com/v2/venues/search"
    query = parse.urlencode({
        "ll": str(lat) + "," + str(lng),
        "radius": 10,
        "intent": "checkin",
        "address": address,
        "client_id": client_id,
        "client_secret": client_secret,
        "v": datetime.utcnow().strftime("%Y%m%d"),
        "limit": 5,
    })
    url = url + "?" + query

    with request.urlopen(url) as req:
        return json.loads(req.read().decode("utf-8"))["response"]


def explore_venues(region, client_id=FOURSQUARE_CLIENT, client_secret=FOURSQUARE_SECRET):
    url = "https://api.foursquare.com/v2/venues/search"
    query = parse.urlencode({
        "near": region,
    })


def find_venue(lat, lng, address, **kwargs):
    result = venue_search(lat, lng, address, **kwargs)
    print([venue["location"]["address"] for venue in result['venues']])
    venues = (venue for venue in result["venues"]
              if same_address(address, venue["location"]["address"]))
    try:
        return next(venues)
    except StopIteration:
        return None
