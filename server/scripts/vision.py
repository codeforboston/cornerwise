import base64
import itertools
from math import sqrt

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials, ApplicationDefaultCredentialsError

from PIL import Image

DISCOVERY_URL = "https://{api}.googleapis.com/$discovery/rest?version={apiVersion}"


def get_client():
    creds = GoogleCredentials.get_application_default()
    return discovery.build(
        "vision", "v1", credentials=creds, discoveryServiceUrl=DISCOVERY_URL)


try:
    CLIENT = get_client()
except ApplicationDefaultCredentialsError:
    CLIENT = None


def encode_image(image_file):
    with open(image_file, "rb") as infile:
        return base64.b64encode(infile.read()).decode("ascii")


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
    logos = response.get("logoAnnotations")
    for logo in logos:
        if full_area:
            vertices = logo["boundingPoly"]["vertices"]
            logo_area = (vertices[2]["y"] - vertices[0]["y"]) * (
                vertices[2]["x"] - vertices[0]["x"])
            if logo_area / full_area > 0.5:
                return logo
        elif logo["score"] > 0.80:
            return logo


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
    return ((l["description"], l["score"])
            for l in response["labelAnnotations"])


def process_image(image_file):
    if not CLIENT: return None

    image = Image.open(image_file)
    try:
        response = annotate_image(CLIENT, image_file)["responses"][0]
        return {"logo": find_logo(response)}
    except KeyError:
        return None
