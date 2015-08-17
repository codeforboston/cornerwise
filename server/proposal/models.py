from django.contrib.gis.db import models

class Proposal(models.Model):
    case_number = models.CharField(max_length=64,
                                   unique=True,
                                   help_text="The unique case number assigned by the city")
    address = models.CharField(max_length=128,
                               help_text="Street address")
    location = models.PointField(help_text="The latitude and longitude")
    region_name = models.CharField(max_length=128,
                                   null=True,
                                   help_text="")
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    summary = models.CharField(max_length=256)
    description = models.TextField()
    source = models.URLField(null=True,
                             help_text="The data source for the proposal.")
    status = models.CharField(max_length=64)

class ProposalEvent(models.Model):
    """
    Meeting or hearing associated with a proposal.
    """
    title = models.CharField(max_length=256)
    date = models.DateTimeField()
    duration = models.DurationField(null=True)
    description = models.TextField()
    proposal = models.ForeignKey(Proposal)


class ProposalDocument(models.Model):
    """
    A document associated with a proposal.
    """
    proposal = models.ForeignKey(Proposal)
    event = models.ForeignKey(ProposalEvent, null=True)
    url = models.URLField()
    document = models.FileField(null=True)
