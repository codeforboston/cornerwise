import base64

from urllib import parse, request

def encode_key(api_key):
    return "Basic " + base64.b64encode(":{key}"
                                       .format(key=api_key)
                                       .encode("ascii"))\
                            .decode("ascii")


def sign_request(req, api_key):
    req.add_header("Authorization", encode_key(api_key))
    return req


class SearchApi(object):
    news_url = "https://api.datamarket.azure.com/Bing/Search/News"

    def __init__(self, api_key):
        self.api_key = api_key

    def news_search(self, query,
                    lat=42.371861543730496,
                    lng=-71.13338470458984,
                    loc="US.LA",
                    sort="Date"):
        data = {"Query": '"' + query + '"',
                "Latitude": lat,
                "Longitude": lng,
                "NewsLocationOverride": loc,
                "Sort": sort,
                }
        url = self.news_url + "?" + parse.urlencode(data)
        req = request.Request(url)
        sign_request(req, self.api_key)

        return request.urlopen(req)



