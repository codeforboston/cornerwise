from django.conf import settings
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page

from functools import reduce
from itertools import chain

from shared.request import make_response

from .models import Proposal, Attribute, Document, Event, Image

def proposal_json(proposal, include_images=True, include_attributes=False):
    pdict = model_to_dict(proposal, exclude=["location", "fulltext"])
    pdict["location"] = {"lat": proposal.location.y,
                         "lng": proposal.location.x}

    pdict["documents"] = [d.to_dict() for d in proposal.document_set.all()]

    if include_images:
        images = Image.objects.filter(document__proposal=proposal)
        pdict["images"] = [img.to_dict() for img in images]

    if include_attributes:
        attributes = Attribute.objects.filter(proposal=proposal)
        pdict["attributes"] = [a.to_dict() for a in attributes]

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
        return reduce(lambda q1, q2: q1 & q2, subqueries)

def build_proposal_query(d):
    subqueries = []
    attrs_query = build_attributes_query(d)

    if attrs_query:
        ids = list(chain(*Attribute.objects.filter(attrs_query)\
                         .values_list("proposal_id")))
        subqueries.append(Q(pk__in=ids))

    status = d.get("status", "active").lower()
    if status == "closed":
        subqueries.append(Q(complete=True))
    elif status == "active":
        subqueries.append(Q(complete=False))

    return reduce(lambda q1, q2: q1 & q2, subqueries, Q())


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
        # Server the file using mod_xsendfile
        pass

    return FileResponse(doc.document)
