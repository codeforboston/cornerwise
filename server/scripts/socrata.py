import base64, json, re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

accepts = {
    "json": "application/json",
    "xml": "application/xml"
}

def make_request(domain, resource_id, token, fmt="json"):
    url = "https://{domain}/resource/{resource_id}.{fmt}"\
          .format(domain=domain,
                  resource_id=resource_id,
                  fmt=fmt)
    data = None

    return Request(url, data, {"Accept": accepts[fmt],
                               "X-App-Token": token})


def do_get(*args, **kwargs):
    req = make_request(*args, **kwargs)
    f = urlopen(req)
    body = f.read().decode("utf-8")
    json_response = json.loads(body)
    f.close()

    return json_response
