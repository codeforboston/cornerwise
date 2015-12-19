from django.conf import settings
from django.contrib.gis.geos.polygon import Polygon
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page

from collections import defaultdict
from functools import reduce
from itertools import chain
import re

from shared.request import make_response

from .models import Proposal, Attribute, Document, Event, Image

default_attributes = [
    "applicant_name"
]

def proposal_json(proposal, include_images=True,
                  include_attributes=default_attributes,
                  include_events=False, include_documents=True):
    pdict = model_to_dict(proposal, exclude=["location", "fulltext"])
    pdict["location"] = {"lat": proposal.location.y,
                         "lng": proposal.location.x}

    if include_documents:
        pdict["documents"] = [d.to_dict() for d in proposal.document_set.all()]

    if include_images:
        pdict["images"] = [img.to_dict() for img in \
                           proposal.images.order_by("-priority")]

    if include_attributes:
        attributes = Attribute.objects.filter(proposal=proposal)
        if include_attributes is not True:
            attributes = attributes.filter(handle__in=include_attributes)
        pdict["attributes"] = [a.to_dict() for a in attributes]

    if include_events:
        pdict["events"] = [e.to_dict for e in proposal.events.all()]

    return pdict


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
    "region": "region_name",
    "case": "case_number",
    "address": "address"
}

def build_proposal_query(d):
    subqueries = {}
    ids = build_attributes_query(d) or []

    pids = d.get("id")
    if pids:
        ids = re.split(r"\s*,\s*", pids)

    if ids:
        subqueries["pk__in"] = ids

    bounds = d.get("bounds")
    if bounds:
        coords = [float(coord) for coord in bounds.split(",")]
        bbox = Polygon.from_bbox(*coords, srid=97406)
        subqueries["location__within"] = bbox

    status = d.get("status", "active").lower()
    if status == "closed":
        subqueries["complete"] = True
    elif status == "active":
        subqueries["complete"] = False
    # If status is anything other than 'active' or 'closed', find all
    # proposals.

    event = d.get("event")
    if event:
        try:
            subqueries["event"] = int(event)
        except ValueError as verr:
            pass

    for k in d:
        if k in query_params:
            subqueries[query_params[k]] = d[k]

    return Q(**subqueries)


@make_response()
def active_proposals(req):
    proposals = Proposal.objects.filter(build_proposal_query(req.GET))

    return {"proposals": list(map(proposal_json, proposals))}


@make_response()
def closed_proposals(req):
    proposals = Proposal.objects.filter(complete=True)

    return {"proposals": list(map(proposal_json, proposals))}


@make_response()
def view_proposal(req, pk=None):
    if not pk:
        pk = req.GET.get("pk")

    proposal = get_object_or_404(Proposal, pk=pk)

    return proposal_json(proposal, include_attributes=True)


# Document views
@make_response()
def view_document(req, pk):
    "Retrieve details about a Document."
    doc = get_object_or_404(Document, pk=pk)

    return doc.to_dict()


def download_document(req, pk):
    doc = get_object_or_404(Document, pk=pk)

    if not doc.document:
        return {}

    if settings.IS_PRODUCTION:
        # Serve the file using mod_xsendfile
        pass

    return FileResponse(doc.document)
