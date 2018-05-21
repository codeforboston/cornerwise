from django.db.models import Q
from django.utils import timezone
import calendar
from collections import defaultdict
from datetime import datetime, timedelta
from functools import reduce
import re

from dateutil.parser import parse as parse_date

from .models import Attribute, local_now, localize_dt
from parcel.models import LotSize, LotQuantiles
from utils import bounds_from_box, point_from_str


# TODO: Rewrite considering parcels
def get_lot_size_groups():
    quantiles = LotQuantiles.objects.all()[0]
    return {
        "small": {"lot_size__lte": quantiles.small_lot},
        "medium": {"lot_size__lte": quantiles.medium_lot,
                   "lot_size__gt": quantiles.small_lot},
        "large": {"lot_size__gt": quantiles.medium_lot}
    }

LOT_SIZES = None

def get_lot_sizes():
    global LOT_SIZES
    if not LOT_SIZES:
        LOT_SIZES = get_lot_size_groups()

    return LOT_SIZES


def make_size_query(param):
    size_query = get_lot_sizes().get(param.lower())
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


def month_range(dt):
    _, days = calendar.monthrange(dt.year, dt.month)
    start = dt.replace(day=1)
    return (start, start+timedelta(days=days))


def time_query(d):
    if "month" in d:
        dt = parse_date(d["month"])
        start, end = month_range(dt)
    elif "start" in d:
        start = parse_date(d["start"])
        end = "end" in d and parse_date(d["end"])
    else:
        return None

    if "region" in d:
        region = d["regions"].split(";", 1)[0].strip()
    else:
        region = None

    start = localize_dt(start, region)
    end = localize_dt(end, region) if end else local_now(region)

    return start, end


# If any of these params is specified in the query, look for Proposals where
# the field matches literally.
query_params = {
    "case": "case_number",
    "address": "address",
    "source": "source"
}


def build_proposal_query_dict(d):
    subqueries = {}
    ids = run_attributes_query(d) or []
    defaults = {"status": "active"}

    if "id" in d:
        ids = re.split(r"\s*,\s*", d["id"])

    if "text" in d:
        subqueries["address__icontains"] = d["text"]

    if d.get("region"):
        regions = re.split(r"\s*;\s*", d["region"])
        subqueries["region_name__in"] = regions

    if ids:
        subqueries["pk__in"] = ids

    time_range = time_query(d)
    if time_range:
        (start_date, end_date) = time_range
        subqueries["created__gte"] = start_date
        subqueries["created__lt"] = end_date

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

    if "parcel" in d:
        subqueries["parcel__pk__in"] = d["parcel"].split(",")
        defaults["status"] = "all"

    if "box" in d:
        subqueries["location__within"] = bounds_from_box(d["box"])
    elif "center" in d and "r" in d:
        subqueries["location__distance_lte"] = (point_from_str(d["center"]),
                                                float(d["r"]))

    if "event" in d:
        subqueries["event__in"] = d["event"].split(",")
        defaults["status"] = "all"

    # If status is anything other than 'active' or 'closed', find all
    # proposals.
    status = d.get("status", defaults["status"]).lower()
    if status == "closed":
        subqueries["complete__isnull"] = False
    elif status == "active":
        subqueries["complete__isnull"] = True

    for k in d:
        if k in query_params:
            subqueries[query_params[k]] = d[k]

    return subqueries


def build_proposal_query(d):
    subqueries = build_proposal_query_dict(d)
    return Q(**subqueries)


def build_event_query(d):
    subqueries = {}
    if "region" in d:
        subqueries["region_name__in"] = re.split(r"\s*;\s*", d["region"])

    time_range = time_query(d)
    if time_range:
        start, end = time_range
        subqueries["date__gte"] = start
        subqueries["date__lt"] = end
    else:
        subqueries["date__gte"] = timezone.now()

    if "proposal" in d:
        subqueries["proposals__pk__in"] = d["proposal"].split(",")

    return Q(**subqueries)
