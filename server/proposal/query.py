from django.contrib.gis.geos.polygon import Polygon
from django.db.models import Q
from collections import defaultdict
from functools import reduce
import re

from .models import Attribute


def build_attributes_query(d):
    """Construct a Proposal query from query parameters.

    :param d: A dictionary-like object, typically something like
    request.GET.

    :returns: A
    """
    # Query attributes:
    subqueries = []

    for k, val in d.items():
        if not k.startswith("attr."):
            continue

        subqueries.append(Q(handle=k[5:], text_value__contains=val))

    if subqueries:
        query = reduce(Q.__or__, subqueries, Q())
        attrs = Attribute.objects.filter(query)\
                                 .values("proposal_id", "handle",
                                         "text_value")
        attr_maps = defaultdict(int)
        for attr in attrs:
            attr_maps[attr["proposal_id"]] += 1

        return [pid for pid, c in attr_maps.items() if c == len(subqueries)]


query_params = {
    "case": "case_number",
    "address": "address",
    "source": "source"
}

# TODO: Don't hardcode this
region_names = {"somerville": "Somerville, MA", "cambridge": "Cambridge, MA"}


def build_proposal_query_dict(d):
    subqueries = {}
    ids = build_attributes_query(d) or []

    if "id" in d:
        ids = re.split(r"\s*,\s*", d["id"])

    if "text" in d:
        subqueries["address__icontains"] = d["text"]

    if d.get("region"):
        regions = re.split(r"\s*,\s*", d["region"])
        regions = [region_names[r] for r in regions if r in region_names]
        if len(regions) == 1:
            subqueries["region_name"] = regions[0]
        else:
            subqueries["region_name__in"] = regions

    if ids:
        subqueries["pk__in"] = ids

    if "projects" in d:
        if d["projects"] == "null":
            subqueries["project__isnull"] = True
        elif d["projects"] == "all":
            subqueries["project__isnull"] = False
        # else:
        #     subqueries["projects"] = d["project"]

    bounds = d.get("box")
    if bounds:
        coords = [float(coord) for coord in bounds.split(",")]
        # Coordinates are submitted to the server as
        # latMin,longMin,latMax,longMax, but from_bbox wants its arguments in a
        # different order:
        bbox = Polygon.from_bbox((coords[1], coords[0], coords[3], coords[2]))
        subqueries["location__within"] = bbox

    # If status is anything other than 'active' or 'closed', find all
    # proposals.
    status = d.get("status", "active").lower()
    if status == "closed":
        subqueries["complete"] = True
    elif status == "active":
        subqueries["complete"] = False

    event = d.get("event")
    if event:
        try:
            subqueries["event"] = int(event)
        except ValueError:
            pass

    for k in d:
        if k in query_params:
            subqueries[query_params[k]] = d[k]

    return subqueries


def build_proposal_query(d):
    subqueries = build_proposal_query_dict(d)
    return Q(**subqueries)
