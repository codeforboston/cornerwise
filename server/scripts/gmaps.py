import json
import threading
from queue import Queue

from urllib.parse import urlencode
from urllib.request import urlopen

def geocode(api_key, address):
    data = (
        ("key", api_key),
        ("address", address),
    )
    url = "https://maps.googleapis.com/maps/api/geocode/json?" + urlencode(data)

    f = urlopen(url)
    body = f.read().decode("utf-8")
    json_response = json.loads(body)

    if json_response["status"] == "OK":
        return json_response["results"][0]

def simplify(result):
    """Takes a dictionary as returned from the Google Maps geocoder API and
returns a flattened dict conforming to the generic geocoder expectations.
    """
    return {
        "location": result["geometry"]["location"],
        "formatted_name": result["formatted_address"],
        "properties": {
            "place_id": result["place_id"],
            "types": result["types"]
        }
    }

class GeocoderThread(threading.Thread):
    def __init__(self, addr_q, out, geocoder):
        self.addr_q = addr_q
        self.out = out
        self.geocoder = geocoder
        super().__init__()

    def start(self):
        while True:
            address = self.addr_q.get_nowait()

            if not address:
                break

            try:
                print("Geocoding address:", address)
                result = geocode(self.geocoder.api_key, address)
                self.out.append((address, simplify(result)))
            except Exception as err:
                print("Error in thread", self, err)
            finally:
                self.addr_q.task_done()


class GoogleGeocoder(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def geocode_threaded(self, addrs, parallelism=5):
        address_q = Queue(len(addrs))
        for addr in addrs: address_q.put_nowait(addr)

        # Use a list to collect results, because .append() is
        # thread-safe
        out = []

        for i in range(parallelism):
            gt = GeocoderThread(address_q, out, self)
            gt.start()

        address_q.join()

        # Out is a list of pairs of (addr, result)
        results = dict(out)

        # Pluck out the results in the same order as the input
        # addresses:
        return [results[a] for a in addrs]

    def geocode(self, addrs):
        results = []
        for addr in addrs:
            results.append(simplify(geocode(self.api_key, addr)))
        return results
