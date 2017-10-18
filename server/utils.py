from datetime import datetime
import json
import os
import re
import pytz
from collections import deque
from urllib import parse, request

from django.contrib.gis.geos import GeometryCollection, GEOSGeometry
from django.contrib.gis.geos.polygon import Polygon


def normalize(s):
    """
    Downcases string s, removes special characters and replaces spaces with _.

    :s: a string
    """
    s = re.sub(r"[',!@#$%^&*()-=[\]]+", "", s)
    s = re.sub(r"\s+", "_", s)

    return s.lower()


def extension(path):
    "Returns the last piece of the filename after the extension separator."
    return path.split(os.path.extsep)[-1].lower()


class pushback_iter(object):
    """An iterator that implements a pushback() method, allowing values to
be added back to the 'stack' after consideration.
    """
    def __init__(self, it):
        """
        :it: an iterable object
        """
        self.iterable = iter(it)
        self.pushed = deque()

    def pushback(self, v):
        self.pushed.append(v)

    def __iter__(self):
        return self

    def __next__(self):
        if self.pushed:
            return self.pushed.pop()
        return next(self.iterable)


def make_file_mover(attr):
    """Returns a function that takes an object and a new name and renames
    the file associated with that object's `attr` file field.

    :param attr: The name of the FileField attribute on the target
    object

    :returns: A function that can be bound as a method of an object with
    the named file field.

    """
    def move_file(self, new_path):
        file_field = getattr(self, attr)
        current_path = file_field and file_field.path

        if not current_path:
            raise IOError("")

        if os.path.basename(new_path) == new_path:
            doc_dir, _ = os.path.split(current_path)
            new_path = os.path.join(doc_dir, new_path)

        if new_path != current_path:
            os.rename(current_path, new_path)

            try:
                setattr(self, attr, new_path)
                self.save()
            except Exception as err:
                os.rename(new_path, self.local_file)

                raise err

        return new_path

    return move_file


def decompose_coord(ll):
    """
    :ll: degrees latitude or longitude.

    Return a tuple of (degrees, minutes, seconds)
    """
    degrees = int(ll)
    minutes = ll % 1 * 60
    seconds = minutes % 1 * 60

    return (degrees, int(minutes), seconds)


prettify_format = "{d}\N{DEGREE SIGN} {m}' {s:.2f}\" {h}"


def prettify_lat(lat):
    """
    :lat: degrees latitude

    Returns a human-friendly string representing latitude
    """
    d, m, s = decompose_coord(lat)

    return prettify_format.\
        format(d=d, m=m, s=s, h="N" if lat > 0 else "S")


def prettify_long(lng):
    """
    :lng: degrees longitude

    Returns a human-friendly string representing longitude
    """
    d, m, s = decompose_coord(lng)

    return prettify_format.\
        format(d=d, m=m, s=s, h="E" if lng > 0 else "W")


def add_params(url, extra_params):
    """Given a URL, add new query parameters by merging in the contents of the
    `extra_params` dictionary.

    :param url: (str)
    :param extra_params: (dict)

    :returns: (str) URL including new parameters
    """
    parsed = parse.urlparse(url)._asdict()
    params = parse.parse_qs(parsed["query"])
    params.update(extra_params)
    parsed["query"] = parse.urlencode(params, doseq=True)

    return parse.urlunparse(parse.ParseResult(**parsed))


def bounds_from_box(box):
    """Converts a `box` string parameter to a Polygon object.

    :param box: (str) with the format latMin,longMin,latMax,longMax
    """
    coords = [float(coord) for coord in box.split(",")]
    assert len(coords) == 4
    # Coordinates are submitted to the server as
    # latMin,longMin,latMax,longMax, but from_bbox wants its arguments in a
    # different order:
    return Polygon.from_bbox((coords[1], coords[0], coords[3], coords[2]))


def _geometry(feat):
    if feat["type"] == "FeatureCollection":
        return sum([_geometry(f) for f in feat["features"]], [])

    return [GEOSGeometry(json.dumps(feat["geometry"]))]


def geometry(feat):
    return GeometryCollection(_geometry(feat), srid=4326)


def geometry_from_url(url):
    with request.urlopen(url) as resp:
        raw = resp.read().decode("utf-8")
        return geometry(json.loads(raw))


def utc_now():
    return pytz.utc.localize(datetime.utcnow())


def lazy(fn):
    memo = [None, False]

    def wrapped():
        if not memo[1]:
            memo[0:2] = fn(), True
        return memo[0]
    return wrapped
