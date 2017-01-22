from datetime import datetime
import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from shared.address import same_address


FOURSQUARE_URL = "https://api.foursquare.com/v2/venues/search"


def find_venues(params, client_id, client_secret):
    data = [
        ("intent", "checkin"),
        ("radius", params.get("radius", "20")),
        ("address", params.get("address")),
        ("client_id", client_id),
        ("client_secret", client_secret),
        ("v", datetime.now().strftime("%Y%m%d"))]

    try:
        data.append(
            ("ll", "{lat},{lng}".format(lat=params["lat"],
                                        lng=params["lng"])))
    except KeyError:
        pass

    if "near" in params:
        data.append(("near", params["near"]))

    url = "{base}?{query}".format(base=FOURSQUARE_URL,
                                  query=urlencode(data))
    try:
        f = urlopen(url)
    except HTTPError as error:
        if error.code == 400:
            return False, json.loads(error.fp.read().decode())
        return False, error
    json_response = json.loads(f.read().decode("utf-8"))

    try:
        venues = True, json_response["response"]["venues"]
        return venues
    except KeyError:
        return False, None


def find_venue(params, *args):
    found, venues = find_venues(params, *args)
    if found:
        if "address" in params:
            matching_venues = (v for v in venues if
                               same_address(params["address"], v["location"]["address"]))
            try:
                return next(matching_venues)
            except StopIteration:
                return None

        return venues[0] if venues else None

    return None

