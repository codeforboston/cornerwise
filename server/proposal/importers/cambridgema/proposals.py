from urllib import parse
from urllib.request import Request, urlopen
import json
import re

accepts = {
    "json": "application/json",
    "xml": "application/xml"
}


def under_to_title(s):
    return " ".join(word.capitalize() for word in re.split(r"_+", s))


def make_request(domain, resource_id, token, fmt="json",
                 soql=None):
    if soql:
        qs = "?" + parse.urlencode({"$query": soql})
    else:
        qs = ""
    url = "https://{domain}/resource/{resource_id}.{fmt}{qs}"\
          .format(domain=domain,
                  resource_id=resource_id,
                  fmt=fmt,
                  qs=qs)
    data = None

    return Request(url, data, {"Accept": accepts[fmt],
                               "X-App-Token": token})


def get_json(req):
    f = urlopen(req)
    body = f.read().decode("utf-8")
    json_response = json.loads(body)
    f.close()

    return json_response


class Importer(object):
    region_name = "Cambridge, MA"
    domain = "data.cambridgema.gov"

    def __init__(self, api_key, resource="urfm-usws"):
        self.api_key = api_key
        self.resource_id = resource

    def updated_since(self, dt):
        soql = "SELECT * WHERE applicationdate >= '{dt}' OR decisiondate >= '{dt}"\
            .format(dt=dt.isoformat())

        req = make_request(self.domain, self.resource_id, self.api_key,
                           soql=soql)
        json = get_json(req)
        return map(self.process_json, json)

    copy_keys = {
        "caseNumber": "plan_number",
        "status": "status"
    }
    remap_attributes = {
        "Legal Notice": "description",
        "Type": "type",
        "Reason": "reason_for_petition_other"
    }

    def process_json(self, json):
        """
        Process a single 
        """
        proposal = {}

        for kp, kj in self.copy_keys.items():
            proposal[kp] = json[kj]

        proposal["region_name"] = "Cambridge, MA"
        proposal["source"] = "data.cambridgema.gov"

        proposal["attributes"] = {pk: json[k] for pk, k in
                                  self.remap_attributes.items()}


        return proposal
