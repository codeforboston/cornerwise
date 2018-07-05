from django.db.models import Q
from django.utils import timezone
import calendar
from collections import defaultdict
from datetime import datetime, timedelta
from functools import reduce, partial
import re

from dateutil.parser import parse as parse_date

from .models import Attribute, local_now, localize_dt
from parcel.models import LotSize, LotQuantiles
from utils import bounds_from_box, distance_from_str, point_from_str


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

        if k == "attr.*":
            subqueries.append(Q(text_value__search=val))
        else:
            subqueries.append(Q(handle=k[5:], text_value__search=val))

    if subqueries:
        query = reduce(Q.__or__, subqueries, Q())
        attrs = Attribute.objects.filter(hidden=False)\
                                 .filter(query)\
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


def offset(dt, s, op=lambda x, y: x-y):
    days = months = years = 0
    for m in re.finditer(r"(-?\d+)([dmy])", s):
        n = int(m.group(1))
        t = m.group(2)
        if t == "d":
            days += n
        elif t == "m":
            months += n
        elif t == "y":
            years += n

    newmonth = op(dt.month, months)
    return dt.replace(year=op(dt.year, years) + (newmonth//12 if newmonth else -1),
                      month=newmonth%12 or 12) - timedelta(days=days)


def time_query(d):
    if "region" in d:
        region = d["region"].split(";", 1)[0].strip()
    else:
        region = None
    now = local_now(region)
    parse = partial(parse_date,
                    default=now.replace(month=1, day=1, hour=0, minute=0,
                                        second=0, microsecond=0, tzinfo=None))

    start = end = None
    if "month" in d:
        dt = parse(d["month"])
        start, end = month_range(dt)
    elif "start" in d:
        start = parse(d["start"])
        end = "end" in d and parse(d["end"])
    elif "timerange" in d:
        if "-" in d["timerange"]:
            start_spec, end_spec = re.split(r"\s*-\s*", d["timerange"])
            start = parse(start_spec) if start_spec else None
            end = parse(end_spec) if end_spec else None
        else:
            m = re.match(r"([><])((-?\d+[dmy])+|.*)", d["timerange"])
            if m:
                offset_dt = offset(now, m.group(2))
                if m.group(1) == ">":
                    return (offset_dt, None)
                else:
                    return (None, offset_dt)

    start = start and localize_dt(start, region)
    end = end and localize_dt(end, region)

    return start, end


# If any of these params is specified in the query, look for Proposals where
# the field matches literally.
query_params = {
    "case": "case_number",
    "address": "address",
    "source": "source"
}


def build_proposal_query_dict(d):
    """Constructs the keyword arguments to a Django ORM query from a dict passed in
    by a user, either directly from a request or from a saved query, such as a
    Subscription. All keys and values in the dict are expected to be strings.

    Keys considered:

    - id: comma-separated Proposal pks
    - text
    - region
    - month - date string
    - start[/end] - date strings
    - box - swlat,swlng,nelat,nelng
    - center/r - lat,lng / distance string (e.g., 300ft)
    - parcel: comma-separated Parcel pks
    - event: comma-separated Event pks
    - status: "closed"/"active"/"all"

    """
    subqueries = {}
    defaults = {"status": "active"}

    ids = run_attributes_query(d)

    if ids is not None:
        defaults["status"] = "all"

    if "id" in d:
        defaults["status"] = "all"
        pids = re.split(r"\s*,\s*", d["id"])
        ids = pids if ids is None else [id for id in pids if id in set(ids)]

    if "text" in d:
        subqueries["address__icontains"] = d["text"]

    if d.get("region"):
        regions = re.split(r"\s*;\s*", d["region"])
        subqueries["region_name__in"] = regions

    if ids is not None:
        subqueries["pk__in"] = ids

    (start_date, end_date) = time_query(d)
    if start_date:
        subqueries["started__gte"] = start_date
    if end_date:
        subqueries["started__lt"] = end_date

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
                                                distance_from_str(d["r"]))

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

    (start, end) = time_query(d)
    if start or end:
        if start:
            subqueries["date__gte"] = start
        if end:
            subqueries["date__lt"] = end
    else:
        subqueries["date__gte"] = timezone.now()

    if "proposal" in d:
        subqueries["proposals__pk__in"] = d["proposal"].split(",")

    return Q(**subqueries)
