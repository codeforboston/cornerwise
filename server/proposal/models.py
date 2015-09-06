from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.db.models import Q

class ProposalManager(models.GeoManager):
    def between(self, start=None, end=None):
        q = None

        if start:
            q = Q(created__gte=start)

        if end:
            endQ = Q(closed_lte=end)

            if q:
                q = Q & endQ
            else:
                q = endQ

        return self.objects.filter(q)

    def build_query(self, params):
        "Construct a query from parameters passed in "
        pass

    def for_parcel(self, parcel):
        return self.filter(location__within=parcel.shape)

class Proposal(models.Model):
    case_number = models.CharField(max_length=64,
                                   unique=True,
                                   help_text="The unique case number assigned by the city")
    address = models.CharField(max_length=128,
                               help_text="Street address")
    location = models.PointField(help_text="The latitude and longitude")
    region_name = models.CharField(max_length=128,
                                   # Hardcode this for now
                                   default="Somerville, MA",
                                   null=True,
                                   help_text="")
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
#    closed = models.DateTimeField(null=True,
                                  #help_text="The time when this proposal was closed.")
    summary = models.CharField(max_length=256)
    description = models.TextField()
    source = models.URLField(null=True,
                             help_text="The data source for the proposal.")
    status = models.CharField(max_length=64)

    # To enable geo queries
    objects = ProposalManager()

    def get_absolute_url(self):
        return reverse("view-proposal",
                       kwargs={"pk": self.pk})


class Event(models.Model):
    """
    Meeting or hearing associated with a proposal.
    """
    title = models.CharField(max_length=256)
    date = models.DateTimeField()
    duration = models.DurationField(null=True)
    description = models.TextField()
    proposal = models.ForeignKey(Proposal)

class Document(models.Model):
    """
    A document associated with a proposal.
    """
    proposal = models.ForeignKey(Proposal)
    event = models.ForeignKey(Event, null=True,
                              help_text="Event associated with this document")
    url = models.URLField()
    title = models.CharField(max_length=256,
                             help_text="The name of the document")
    field = models.CharField(max_length=256,
                             help_text="The field in which the document was found")
    # Record when the document was first observed:
    created = models.DateTimeField(auto_now_add=True)
    document = models.FileField(null=True)

    class Meta:
        # Ensure at the DB level that documents are not duplicated:
        unique_together = (("proposal", "url"))

class Image(models.Model):
    """An image associated with a document. In the future, it may be
    worthwhile to alter this to allow images associated directly with a
    proposal.

    """
    document = models.ForeignKey(Document)
    image = models.FileField()
    created = models.DateTimeField(auto_now_add=True)
