import base64
import json
from urllib import parse, request


class AzureTextAnalyzer(object):
    base_url = "https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/"
    v1_base_url = "https://api.datamarket.azure.com/data.ashx/amla/text-analytics/v1/"

    def __init__(self, api_key):
        self.api_key = api_key

    def sign_request(self, req):
        enc = ("AccountKey:" + self.api_key).encode("utf-8")
        auth = base64.b64encode(enc).decode("ascii")
        req.headers["Authorization"] = f"Basic {auth}"
        return req

    def make_v1_request(self, op, params):
        url = self.v1_base_url + op + "?" + parse.urlencode(params)
        req = self.sign_request(
            request.Request(url, headers={"Accept": "application/json"}))
        return request.urlopen(req)

    def get_v1_key_phrases(self, text):
        with self.make_request("GetKeyPhrases", {"Text": text}) as resp:
            json_str = resp.read().decode("utf-8")
            return json.loads(json_str)["KeyPhrases"]

    def make_request(self, op, params={}, data=None, content_type="application/json"):
        req = request.Request(
            self.base_url + op + "?" + parse.urlencode(params),
            method="POST",
            data=data,
            headers={"Ocp-Apim-Subscription-Key": self.api_key,
                     "Content-Type": content_type})
        self.sign_request(req)
        return request.urlopen(req)

    def make_document(self, text, doc_id="1", language="en"):
        return { "language": language,
                 "id": doc_id,
                 "text": text }

    def get_key_phrases(self, text):
        input = {"documents": [self.make_document(text)]}
        req = self.make_request("keyPhrases", data=json.dumps(input).encode())
        response = json.loads(req.read())
        try:
            return response["documents"][0]["keyPhrases"]
        except IndexError:
            raise Exception(response["errors"])
        except KeyError:
            return []


class GoogleTextAnalyzer(object):
    url = "https://language.googleapis.com/v1/documents:analyzeEntities"
    def __init__(self, api_key):
        self.api_key = api_key

    def get_key_phrases(self, text):
        body = {"encodingType": "UTF8",
                "document": {"type": "PLAIN_TEXT", "content": text}}
        query = {"key": self.api_key}
        req = request.Request(self.url + "?" + parse.urlencode(query),
                              data=json.dumps(body).encode(),
                              headers={"Content-Type": "application/json"},
                              method="POST")
        body = request.urlopen(req).read()
        response = json.loads(body)
        return response
