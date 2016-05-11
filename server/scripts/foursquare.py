from datetime import datetime
import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen


FOURSQUARE_URL = "https://api.foursquare.com/v2/venues/search"


def find_venue(params, client_id, client_secret):
    data = [
        ("intent", "browse"),
        ("radius", params.get("radius", "20")),
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
    return True, json_response

    try:
        venues = json_response["response"]["venues"]
        return venues
    except KeyError:
        return None
