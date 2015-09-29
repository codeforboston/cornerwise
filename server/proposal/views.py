from django.conf import settings
from django.forms.models import model_to_dict
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page

from shared.request import make_response

from .models import Proposal, Attribute, Document, Event, Image

#@make_response()
#def

def proposal_json(proposal, include_images=True, include_attributes=False):
    pdict = model_to_dict(proposal, exclude=["location", "fulltext"])
    pdict["location"] = {"lat": proposal.location.y,
                         "lng": proposal.location.x}
    # TODO: If the document has been copied to the server, return
    # document.document.url instead of document.url as the URL.
    pdict["documents"] = [d.to_dict() for d in proposal.document_set.all()]

    if include_images:
        images = Image.objects.filter(document__proposal=proposal)
        pdict["images"] = [img.image.url for img in images]

    if include_attributes:
        attributes = Attribute.objects.filter(proposal=proposal)
        pdict["attributes"] = [a.to_dict() for a in attributes]

    return pdict

@make_response()
def active_proposals(req):
    proposals = Proposal.objects.filter(status="", complete=False)

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
