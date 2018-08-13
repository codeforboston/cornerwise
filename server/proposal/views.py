from celery import shared_task
from functools import reduce
import json
from operator import or_
from urllib import parse

from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse

from shared.request import make_response, ErrorResponse

from .models import Proposal, Attribute, Document, Event, Image, Layer
from .query import build_proposal_query, build_event_query
from utils import bounds_from_box, add_params

default_attributes = [
    "applicant_name", "legal_notice"
]


def proposal_json(proposal,
                  include_images=True,
                  include_attributes=default_attributes,
                  include_events=False,
                  include_documents=True,
                  include_projects=True):
    pdict = model_to_dict(proposal, exclude=["location", "fulltext"])
    pdict["location"] = {
        "lat": proposal.location.y,
        "lng": proposal.location.x
    }

    if include_documents:
        pdict["documents"] = [d.to_dict() for d in proposal.documents.all()]

    if include_images:
        images = proposal.images.order_by("-priority")
        # Booleans are considered integers
        if isinstance(include_images, int) and include_images is not True:
            images = images[0:include_images]

        pdict["images"] = [img.to_dict() for img in images]

    if include_attributes:
        attributes = proposal.attributes.filter(hidden=False)
        if include_attributes is not True:
            attributes = attributes.filter(handle__in=include_attributes)
        pdict["attributes"] = [a.to_dict() for a in attributes]

    if include_events:
        pdict["events"] = [e.to_json_dict() for e in proposal.events.all()]

    if include_projects and proposal.project:
        pdict["project"] = proposal.project.to_dict()

    # TODO: Filter on parcel attributes

    # TODO: fulltext query

    return pdict


def layer_json(layer):
    return {"name": layer.name,
            "icon_text": layer.icon_text,
            "icon": layer.icon.url,
            "url": layer.url,
            "region_name": layer.region_name}


def _query(req):
    queries = req.GET.getlist("query")
    if queries:
        query = reduce(or_, (build_proposal_query(json.loads(q))
                             for q in queries), Q())
    else:
        query = build_proposal_query(req.GET)
    proposals = Proposal.objects.filter(query)
    if "include_projects" in req.GET:
        proposals = proposals.select_related("project")
    return proposals


def paginator_context(page, page_url=lambda page: f"?page={page}"):
    next_page = page.has_next() and page.next_page_number()
    prev_page = page.has_previous() and page.previous_page_number()
    return {
        "count": page.paginator.count,
        "total_pages": page.paginator.num_pages,
        "page": page.number,
        "next_page": next_page,
        "next_url": next_page and page_url(next_page),
        "prev_page": "",
        "prev_url": prev_page and page_url(prev_page),
        "per_page": page.paginator.per_page
    }


# Views:
@make_response("list.djhtml")
def list_proposals(req):
    proposals = _query(req)

    try:
        page = int(req.GET["page"])
    except (ValueError, KeyError):
        page = 1

    context = {}

    if page:
        try:
            per_page = int(req.GET.get("per_page", 50))
        except ValueError:
            per_page = 50
        paginator = Paginator(proposals, per_page=min(per_page, 50))
        proposals = paginator.page(page)
        try:
            query_params = req.GET.copy()
            def make_url(page):
                query_params["page"] = str(page)
                return req.path + "?" + query_params.urlencode()

            context["paginator"] = paginator_context(proposals, make_url)
        except (PageNotAnInteger, EmptyPage) as err:
            raise ErrorResponse("No such page", {"page": page}, err=err)

    context["proposals"] = [
        proposal_json(
            proposal, include_images=1, include_events=True) for proposal in proposals
    ]

    return context


@make_response("view.djhtml")
def view_proposal(req, pk=None):
    pk = req.GET.get("pk", pk)
    lookup = req.site_config.query_defaults.copy()
    if pk:
        lookup["pk"] = pk
    else:
        if "case_number" in req.GET:
            lookup["case_number"] = req.GET["case_number"]

    proposal = get_object_or_404(Proposal, **lookup)

    return proposal_json(
        proposal,
        include_attributes=True,
        include_images=True,
        include_events=True)


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


@make_response("layers.djhtml")
def list_layers(req):
    query = {}
    if req.GET.get("box"):
        query["envelope__overlaps"] = bounds_from_box(req.GET.get("box"))
    regions = req.GET.getlist("region_name")
    if regions:
        query["region_name__in"] = regions
    layers = Layer.objects.filter(**query)
    return {"layers": [layer_json(l) for l in layers]}


@make_response("events.djhtml")
def list_events(req):
    query = build_event_query(req.GET)
    events = Event.objects.filter(query).order_by("date")
    title = "Events" if query else "Upcoming Events"

    return {"events": [event.to_json_dict() for event in events],
            "title": title}


@make_response("event.djhtml")
def view_event(req, pk=None):
    if not pk:
        pk = req.GET.get("pk")

    event = get_object_or_404(Event, pk=pk)
    d = event.to_json_dict()
    d["proposals"] = [
        proposal_json(
            p,
            include_images=False,
            include_attributes=["applicant_name", "legal_notice"],
            include_documents=False)
        for p in event.proposals.all().select_related("project")
    ]
    return {"event": d}


@make_response()
def view_image(req, pk=None):
    if not pk:
        pk = req.GET.get("pk")

    image = get_object_or_404(Image, pk=pk)
    return image.to_dict()

@make_response("images.djhtml")
def list_images(req):
    return {"images": Image.objects.exclude(image="")}
