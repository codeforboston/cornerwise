from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page

from shared.request import make_response

from .models import Proposal, Document, Event, Image

#@make_response()
#def

def proposal_json(proposal, include_images=True):
    pdict = model_to_dict(proposal, exclude=["location", "fulltext"])
    pdict["location"] = {"lat": proposal.location.y,
                         "lng": proposal.location.x}
    # TODO: If the document has been copied to the server, return
    # document.document.url instead of document.url as the URL.
    pdict["documents"] = [d.to_dict() for d in proposal.document_set.all()]

    if include_images:
        images = Image.objects.filter(document__proposal=proposal)
        pdict["images"] = [img.image.url for img in images]
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
def view_proposal(req, pk):
    proposal = get_object_or_404(Proposal, pk=pk)

    return {"proposal": proposal_json(proposal)}
