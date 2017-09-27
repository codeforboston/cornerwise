import copy
from decimal import Decimal
from datetime import datetime
import json
import pytz
import re
from urllib import parse
from urllib.request import Request, urlopen


def make_request(domain, resource_id, token, fmt="json",
                 soql=None, exclude_system=True):
    params = {}
    if soql:
        params["$query"] = soql
    if not exclude_system:
        params["$$exclude_system_fields"] = "false"

    qs = ("?" + parse.urlencode(params)) if params else ""
    url = f"https://{domain}/resource/{resource_id}.{fmt}{qs}"
    data = None

    return Request(url, data, {"Accept": "application/json",
                               "X-App-Token": token})


def get_json(req):
    with urlopen(req) as f:
        return json.loads(f.read().decode("utf-8"))


class Importer(object):
    def __init__(self, api_key, resource):
        pass


class Importer(object):
    domain = "data.somervillema.gov"

    def __init__(self, api_key):
        self.api_key = api_key

    copy_keys = {}

    address_key = "address"

    def process_json(self, pjson):
        project = copy.copy(self.constant_fields)

        for project_key, json_key in self.copy_keys.items():
            project[project_key] = pjson.get(json_key)

        try:
            address = pjson[self.address_key]
            if address["needs_recoding"]:
                project["address"] = None
            else:
                human_address = json.loads(address["human_address"])
                project["address"] = human_address["address"]
                project["lat"] = float(address["latitude"])
                project["long"] = float(address["longitude"])
        except:
            project["address"] = None

        self.process(pjson, project)

        return project

    def process(self, json, project):
        pass

    def updated_since(self, dt=None):
        if dt:
            soql = "SELECT * WHERE :updated_at > '{dt}'".\
                   format(dt=dt.isoformat())
        else:
            soql = None
        req = make_request(self.domain, self.resource_id,
                           self.api_key, soql=soql, exclude_system=False)
        projects = get_json(req)

        return [self.process_json(project) for project in projects]
