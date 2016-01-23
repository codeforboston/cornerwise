from dateutil.parser import parse
from urllib import request

def last_modified(url):
    req = request.Request(url=url, method="HEAD")
    with request.urlopen(req) as resp:
        if "Last-Modified" in resp.headers:
            return parse(resp.headers["Last-Modified"])

    return None
