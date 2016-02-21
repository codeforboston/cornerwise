import base64

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

DISCOVERY_URL="https://{api}.googleapis.com/$discovery/rest?version={apiVersion}"

def encode_image(image_file):
    with open(image_file, "rb") as infile:
        return base64.b64encode(infile.read()).decode("ascii")


def annotate_image(vision_client, image_file):
    # TODO: Provide an image context with latLongRect
    body = {
        "requests": [
            {
                "image": {"content": encode_image(image_file)},
                "features": [
                    {"type": "LABEL_DETECTION",
                     "max_results": 5},
                    {"type": "IMAGE_PROPERTIES",
                     "max_results": 5},
                ]
            }]}
    request = vision_client.images().annotate(body=body)
    return request.execute()


def get_client():
    creds = GoogleCredentials.get_application_default()
    return discovery.build("vision", "v1", credentials=creds,
                           discoveryServiceUrl=DISCOVERY_URL)
