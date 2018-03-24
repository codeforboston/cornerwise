import base64
import logging
from collections import OrderedDict
from io import BytesIO
from math import sqrt
from urllib.request import urlopen

from googleapiclient import discovery
from httplib2 import ServerNotFoundError
from oauth2client.client import (ApplicationDefaultCredentialsError,
                                 GoogleCredentials)
from PIL import Image

DISCOVERY_URL = "https://{api}.googleapis.com/$discovery/rest?version={apiVersion}"


def is_streetview_url(url):
    return url.startswith("https://maps.googleapis.com/maps/api/streetview")


def get_client():
    creds = GoogleCredentials.get_application_default()
    return discovery.build(
        "vision", "v1", credentials=creds, discoveryServiceUrl=DISCOVERY_URL)


try:
    CLIENT = get_client()
except (ApplicationDefaultCredentialsError, ServerNotFoundError) as exc:
    logging.warning("Unable to initialize Google Vision client: %s", exc)
    CLIENT = None


def image_similarity(image_path_a, image_path_b):
    image_a = Image.open(image_path_a)
    image_b = Image.open(image_path_b)
    (wA, hA) = image_a.width, image_a.height
    (wB, hB) = image_b.width, image_b.height

    if abs(wA/hA - wB/hB) > 0.1:
        return 0

    scaleA = min()

    a_gray = image_a.convert("LA")
    b_gray = image_b.convert("LA")


def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode("ascii")


def annotate_image(client, image_file):
    # TODO: Provide an image context with latLongRect (?)
    body = {
        "requests": [{
            "image": {
                "content": encode_image(image_file)
            },
            "features": [{
                "type": "LABEL_DETECTION",
            }, {
                "type": "LOGO_DETECTION",
                "max_results": 1
            }, {
                "type": "TEXT_DETECTION"
            }, {
                "type": "IMAGE_PROPERTIES"
            }]
        }]
    }
    request = client.images().annotate(body=body)
    return request.execute()


def find_logo(response, full_width=None, full_height=None):
    """
    Performs some extra processing on the results returned from Google Vision
    API to determine if the logo found in the image (if any) takes up most of
    the area of the image.

    :param response: Response from the Google Vision API
    :param full_width
    :param full_height: Total size of the image

    :returns: if matched, dict with "description", "boundingPoly", and "score"
    fields
    """
    full_area = full_width * full_height if full_width and full_height else None
    logos = response.get("logoAnnotations", [])
    for logo in logos:
        if full_area:
            vertices = logo["boundingPoly"]["vertices"]
            logo_area = (vertices[2]["y"] - vertices[0]["y"]) * (
                vertices[2]["x"] - vertices[0]["x"])
            if logo_area / full_area > 0.5:
                return logo
        elif logo["score"] > 0.80:
            return logo


def find_textual(response, full_width=None, full_height=None):
    for label in response["labelAnnotations"]:
        if label["score"] < 0.85:
            break
        if label["description"] == "text":
            return True

    if "fullTextAnnotation" in response:
        if full_width and full_height:
            total_area = remaining_area = full_width * full_height
            for page in response["fullTextAnnotation"]["pages"]:
                remaining_area -= page["width"] * page["height"]
            if remaining_area/total_area <= 0.8:
                return True


def text(response):
    if "fullTextAnnotation" in response:
        return response["fullTextAnnotation"]["text"]


def rgb_to_xyz(r, g, b):
    def convert(x):
        p = x / 255
        return 100 * (((p * 0.055) / 1.055)
                      **2.4) if p > 0.04045 else (p / 12.92)

    r = convert(r)
    g = convert(g)
    b = convert(b)

    return (r * 0.4124 + g * 0.3576 + b * 0.1805,
            r * 0.2126 + g * 0.7152 + b * 0.0722,
            r * 0.0193 + g * 0.1192 + b * 0.9505)


def xyz_to_lab(x, y, z):
    sqrt_y = sqrt(y)
    return (10 * sqrt_y, # L
            17.5 * (((1.02 * x) - y) / sqrt_y), # a
            7 * ((y - (0.847 * z)) / sqrt_y)) # b


# See https://en.wikipedia.org/wiki/Colorfulness
def perceived_saturation(color):
    (x, y, z) = rgb_to_xyz(color["red"], color["green"], color["blue"])
    (L, a, b) = xyz_to_lab(x, y, z)
    a2_b2 = a*a + b*b
    return 100 * sqrt(a2_b2) / sqrt(L*L + a2_b2)


def colorfulness(response):
    """
    Calculate how colorful an image appears based on the perceived saturation
    of its dominant colors.
    """
    props = response["imagePropertiesAnnotation"]
    colors = props["dominantColors"]["colors"]
    # Total pixel fraction
    total = 0
    total_sat = 0
    for color in colors:
        sat = perceived_saturation(color["color"])
        frac = color["pixelFraction"]
        total_sat += frac*sat
        total += frac

    return total_sat/total


def simplify_labels(response):
    return OrderedDict((l["description"], l["score"])
                       for l in response["labelAnnotations"])


def open_image(image_path=None, image_url=None):
    if image_path:
        return open(image_path, "rb")
    return BytesIO(urlopen(image_url).read())


def process_image(image_path=None, image_url=None):
    assert image_path or image_url
    if not CLIENT:
        return None

    try:
        with open_image(image_path, image_url) as infile:
            response = annotate_image(CLIENT, infile)["responses"][0]
        textual = find_textual(response)
        is_empty_streetview = image_url and is_streetview_url(image_url) and textual
        return {"logo": find_logo(response),
                "colorfulness": colorfulness(response),
                "textual": textual,
                "text": text(response),
                "empty_streetview": is_empty_streetview}
    except KeyError:
        return None
