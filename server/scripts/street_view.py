from base64 import urlsafe_b64decode, urlsafe_b64encode
import hashlib, hmac

from urllib.parse import urlencode

def street_view_url(location, api_key, size="900x600", secret=None):
    data = [
        ("location", location),
        ("key", api_key),
        ("size", size)
    ]
    urlpath = "/maps/api/streetview?" + urlencode(data)

    if secret:
        key = urlsafe_b64decode(secret)
        sig_digest = hmac.new(key, urlpath.encode("utf-8"),
                              hashlib.sha1).digest()
        urlpath += "&signature=" + urlsafe_b64encode(sig_digest).decode("utf-8")

    url = "https://maps.googleapis.com" + urlpath
    return url
