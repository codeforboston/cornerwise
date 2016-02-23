import base64
import json
from urllib import parse, request


class TextAnalyzer(object):
    base_url = "https://api.datamarket.azure.com/data.ashx/amla/text-analytics/v1/"

    def __init__(self, api_key):
        self.api_key = api_key

    def sign_request(self, req):
        enc = ("AccountKey:" + self.api_key).encode("utf-8")
        auth = base64.b64encode(enc).decode("ascii")
        req.headers["Authorization"] = "Basic " + auth
        return req

    def make_request(self, op, params):
        url = self.base_url + op + "?" + parse.urlencode(params)
        req = self.sign_request(
            request.Request(url, headers={"Accept": "application/json"}))
        return request.urlopen(req)

    def get_key_phrases(self, text):
        with self.make_request("GetKeyPhrases", {"Text": text}) as resp:
            json_str = resp.read().decode("utf-8")
            return json.loads(json_str)
