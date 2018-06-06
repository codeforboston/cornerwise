import json
import threading
from queue import Queue

import logging

from urllib.parse import urlencode
from urllib.request import urlopen

import requests

logger = logging.getLogger(__name__)

URL = "https://maps.googleapis.com/maps/api/geocode/json"

def geocode(api_key, address, bounds=None):
    json_response = requests.get(
        URL,
        {"key": api_key,
         "address": address,
         "bounds": bounds or ""}
    ).json()

    if json_response["status"] == "OK":
        return json_response["results"][0]
    else:
        logger.error("Error encountered while geocoding address: " +
                     "{address}\n{error}"
                     .format(address=address, error=json_response))


def simplify(result):
    """Takes a dictionary as returned from the Google Maps geocoder API and
returns a flattened dict conforming to the generic geocoder expectations.
    """
    if result:
        return {
            "location": result["geometry"]["location"],
            "formatted_name": result["formatted_address"],
            "properties": {
                "place_id": result["place_id"],
                "types": result["types"]
            }
        }


def _reverse_geocode(api_key, lat, lng):
    data = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        {"key": api_key, "latlng": f"{lat},{lng}"}
    ).json()

    if data["status"] == "OK":
        return data["results"]

def reverse_geocode(api_key, lat, lng):
    data = _reverse_geocode(api_key, lat, lng)
    if data:
        return data[0]["address_components"]


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
                # Could return None
                self.out.append((address, result and simplify(result)))
            except Exception as err:
                print("Error in thread", self, err)
            finally:
                self.addr_q.task_done()


class GoogleGeocoder(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self._bounds = None

    @property
    def bounds(self):
        return self._bounds

    @bounds.setter
    def bounds(self, bounds):
        "Expects bounds to be in the form [nw-lat, nw-long, se-lat, se-long]"
        self._bounds = "{bounds[0]},{bounds[3]}|{bounds[2]},{bounds[1]}"\
            .format(bounds=bounds)

    def geocode_threaded(self, addrs, parallelism=5):
        address_q = Queue(len(addrs))
        for addr in addrs:
            address_q.put_nowait(addr)

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

    def geocode(self, addrs, bounds=None, region=None):
        results = []
        for addr in addrs:
            if region:
                addr += " " + region
            results.append(simplify(geocode(self.api_key, addr, self.bounds)))
        return results

    def reverse_geocode(self, lat, lng):
        results = _reverse_geocode(self.api_key, lat, lng)
        if results:
            addr = results[0]["formatted_address"]
            return addr
