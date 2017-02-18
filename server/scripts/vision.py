import base64

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


def process_image(image_file):
    if not CLIENT: return None

    image = Image.open(image_file)
    try:
        response = annotate_image(CLIENT, image_file)["responses"][0]
        return {"logo": find_logo(response)}
    except KeyError:
        return None
