import json
from urllib.parse import urlencode
from urllib.request import urlopen

ADDRESS_URL = "http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/geocodeAddresses"
CLIENT_ID = "jYLY7AeA1U9xDiWu"
CLIENT_SECRET = "64a66909ff724a0a9928838ef4462909"
ACCESS_TOKEN = None

def get_access_token():
    global ACCESS_TOKEN

    if ACCESS_TOKEN:
        return ACCESS_TOKEN
    data = urlencode([("grant_type", "client_credentials"),
                      ("client_id", CLIENT_ID),
                      ("client_secret", CLIENT_SECRET)]).\
                      encode("ISO-8859-1")
    f = urlopen("https://www.arcgis.com/sharing/oauth2/token",
                data)
    json_response = json.loads(f.read().decode("utf-8"))

    ACCESS_TOKEN = json_response["access_token"]
    return ACCESS_TOKEN

def geocode(addrs):
    if isinstance(addrs, str):
        addrs = [addrs]

    addresses = json.dumps(
        {"records":
            [{ "attributes":
              {
                "OBJECTID": i+1,
                "Address": addr,
                "City": "Somerville",
                "Region": "MA"
              }
            } for i, addr in enumerate(addrs)]
        })
    data = {
        "addresses": addresses,
        "token": get_access_token(),
        "f": "json"
    }
    #return urlencode(data)
    f = urlopen(ADDRESS_URL, urlencode(data).encode("ISO-8859-1"))
    return json.loads(f.read().decode("utf-8"))
