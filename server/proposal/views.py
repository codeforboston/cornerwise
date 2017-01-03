from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms.models import model_to_dict
from django.http import FileResponse
from django.shortcuts import get_object_or_404

from shared.request import make_response, ErrorResponse

from .models import Proposal, Attribute, Document, Event, Image
from .query import build_proposal_query

default_attributes = [
    "applicant_name", "legal_notice", "dates_of_public_hearing"
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
        pdict["documents"] = [d.to_dict() for d in proposal.document_set.all()]

    if include_images:
        images = proposal.images.order_by("-priority")
        # Booleans are considered integers
        if isinstance(include_images, int) and include_images is not True:
            images = images[0:include_images]

        pdict["images"] = [img.to_dict() for img in images]

    if include_attributes:
        attributes = Attribute.objects.filter(proposal=proposal)
        if include_attributes is not True:
            attributes = attributes.filter(handle__in=include_attributes)
        pdict["attributes"] = [a.to_dict() for a in attributes]

    if include_events:
        pdict["events"] = [e.to_dict() for e in proposal.events.all()]

    if include_projects and proposal.project:
        pdict["project"] = proposal.project.to_dict()

    # TODO: Filter on parcel attributes

    # TODO: fulltext query

    return pdict

# Views:


@make_response("list.djhtml")
def list_proposals(req):
    proposals = Proposal.objects.filter(build_proposal_query(req.GET))
    if "include_projects" in req.GET:
        proposals = proposals.select_related("project")

    pjson = [
        proposal_json(
            proposal, include_images=1) for proposal in proposals
    ]

    return {"proposals": pjson}


@make_response("list.djhtml")
def paginated_active_proposals(req):
    proposal_query = Proposal.objects.filter(build_proposal_query(req.GET))
    if "include_projects" in req.GET:
        proposal_query = proposal_query.select_related("project")
    paginator = Paginator(proposal_query, per_page=100)

    page = req.GET.get("page")
    try:
        proposals = paginator.page(page)
    except PageNotAnInteger:
        proposals = paginator.page(1)
    except EmptyPage as err:
        raise ErrorResponse("No such page", {"page": page}, err=err)

    pjson = [
        proposal_json(
            proposal, include_images=1) for proposal in proposals
    ]

    return {
        "proposals": pjson,
        # "count": proposals.paginator.count,
        "page": proposals.number,
        "total_pages": proposals.paginator.num_pages
    }


@make_response("list.djhtml")
def closed_proposals(req):
    proposals = Proposal.objects.filter(complete=True)

    return {"proposals": list(map(proposal_json, proposals))}


@make_response("view.djhtml")
def view_proposal(req, pk=None):
    if not pk:
        pk = req.GET.get("pk")

    proposal = get_object_or_404(Proposal, pk=pk)

    return proposal_json(
        proposal,
        include_attributes=True,
        include_images=True)


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


@make_response()
def list_events(req):
    events = Event.objects.all().order_by("")

    return {"events": [event.to_dict() for event in events]}


@make_response()
def view_event(req, pk=None):
    if not pk:
        pk = req.GET.get("pk")

    event = get_object_or_404(Event, pk=pk)
    return event.to_dict()


@make_response()
def view_image(req, pk=None):
    if not pk:
        pk = req.GET.get("pk")

    image = get_object_or_404(Image, pk=pk)
    return image.to_dict()
