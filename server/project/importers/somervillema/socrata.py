import copy
from decimal import Decimal
import json
import re
from urllib import parse
from urllib.request import Request, urlopen


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

    return Request(url, data, {"Accept": "application/json",
                               "X-App-Token": token})


def get_json(req):
    with urlopen(req) as f:
        return json.loads(f.read().decode("utf-8"))


class Importer(object):
    domain = "data.somervillema.gov"

    def __init__(self, api_key, resource="wz6k-gm5k"):
        self.api_key = api_key
        self.resource_id = resource

    copy_keys = {
        "name": "project",
        "description": "project_description",
        "justification": "project_justification",
        "department": "department",
        "category": "type",
        "funding_source": "funding_source",
    }

    constant_fields = {
        "region_name": "Somerville, MA"
    }

    @classmethod
    def process_json(kls, pjson):
        project = copy.copy(kls.constant_fields)

        for project_key, json_key in kls.copy_keys.items():
            project[project_key] = pjson.get(json_key)

        project["approved"] = bool(re.match(r"approved", pjson["status"], re.I))

        budget_keys = ((k, re.match(r"^_(\d+)$", k)) for k in pjson.keys())
        project["budget"] = {int(m.group(1)): Decimal(pjson[k])
                             for k, m in budget_keys if m}

        return project

    def updated_since(self, dt=None):
        if dt:
            soql = "SELECT * WHERE :updated_at > '{dt}'".\
                   format(dt=dt.isoformat())
        else:
            soql = None
        req = make_request(self.domain, self.resource_id,
                           self.api_key, soql=soql)
        proposals = get_json(req)

        return map(self.process_json, proposals)
