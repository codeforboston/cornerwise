from django.contrib.gis.geos.polygon import Polygon
from django.db.models import Q
from collections import defaultdict
from functools import reduce
import re

from .models import Attribute
from parcel.models import LotSize, LotQuantiles


def get_lot_size_groups():
    quantiles = LotQuantiles.objects.all()[0]
    return {
        "small": {"lot_size__lte": quantiles.small_lot},
        "medium": {"lot_size__lte": quantiles.medium_lot,
                   "lot_size__gt": quantiles.small_lot},
        "large": {"lot_size__gt": quantiles.medium_lot}
    }

LOT_SIZES = get_lot_size_groups()

def make_size_query(param):
    size_query = LOT_SIZES.get(param.lower())
    if size_query:
        return size_query

    m = re.match(r"([<>])(=?)(\d+(\.\d+)?)", param)
    if m:
        size_op = "lot_size__{op}{eq}".format(
            op="lt" if m.group(1) == "<" else "gt",
            eq="e" if m.group(2) else "")
        return {size_op: float(m.group(3))}


def run_attributes_query(d):
    """Construct a Proposal query from query parameters.

    :param d: A dictionary-like object, typically something like
    request.GET.

    :returns: A
    """
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


def build_proposal_query_dict(d):
    subqueries = {}
    ids = run_attributes_query(d) or []

    if "id" in d:
        ids = re.split(r"\s*,\s*", d["id"])

    if "text" in d:
        subqueries["address__icontains"] = d["text"]

    if d.get("region"):
        regions = re.split(r"\s*;\s*", d["region"])
        subqueries["region_name__in"] = regions

    if ids:
        subqueries["pk__in"] = ids

    if "projects" in d:
        if d["projects"] == "null":
            subqueries["project__isnull"] = True
        elif d["projects"] == "all":
            subqueries["project__isnull"] = False

    if "lotsize" in d:
        parcel_query = make_size_query(d["lotsize"])
        if parcel_query:
            parcel_ids = LotSize.objects.filter(**parcel_query).values("parcel_id")
            subqueries["parcel_id__in"] = parcel_ids

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
