from dateutil.parser import parse
from urllib import request


def last_modified(url):
    req = request.Request(url=url, method="HEAD")
    with request.urlopen(req) as resp:
        if "Last-Modified" in resp.headers:
            return parse(resp.headers["Last-Modified"])

    return None


def doc_info(doc):
    enc = doc.encoding
    if doc.fulltext and doc.fulltext.path:
        lines = (line.decode(enc) for line in doc.fulltext)
    else:
        lines = []

    return {"field": doc.field,
            "title": doc.title,
            "lines": lines}
