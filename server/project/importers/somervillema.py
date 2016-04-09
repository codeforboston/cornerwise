from datetime import datetime
from decimal import Decimal
import pytz
import re

try:
    from .socrata import Importer
except ImportError:
    from socrata import Importer


class SomervilleProjectImporter(Importer):
    domain = "data.somervillema.gov"
    resource_id = "wz6k-gm5k"

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

    address_key = "address"

    def process(self, json, project):
        project["approved"] = bool(re.match(r"approved", json["status"],
                                            re.I))
        project["status"] = json["status"]

        budget_keys = ((k, re.match(r"^_(\d+)$", k)) for k in json.keys())
        project["budget"] = {int(m.group(1)): Decimal(json[k])
                             for k, m in budget_keys if m}
        project["updated"] = datetime.fromtimestamp(json[":updated_at"],
                                                    pytz.utc)

