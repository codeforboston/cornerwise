from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, render

from shared.request import make_response

from .models import Proposal, Document, Event

#@make_response()
#def

def proposal_json(proposal):
    pdict = model_to_dict(proposal, exclude=["location"])
    pdict["location"] = {"lat": proposal.location.y,
                         "lng": proposal.location.x}
    pdict["documents"] = [model_to_dict(d, exclude=["event", "document"]) \
                          for d in proposal.document_set.all()]
    return pdict

@make_response()
def active_proposals(req):
    proposals = Proposal.objects.filter(status="")

    return {"proposals": list(map(proposal_json, proposals))}

@make_response()
def view_proposal(req, pk):
    proposal = get_object_or_404(Proposal, pk=pk)

    return {"proposal": proposal_json(proposal)}
