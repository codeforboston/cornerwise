import os

from django.conf import settings
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.models import model_to_dict

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
        "Construct a query from parameters"
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
    complete = models.BooleanField(default=False)

    # To enable geo queries
    objects = ProposalManager()

    def get_absolute_url(self):
        return reverse("view-proposal",
                       kwargs={"pk": self.pk})

    def document_for_field(self, field):
        return self.document_set.filter(field=field)

class Attribute(models.Model):
    """
    Arbitrary attributes associated with a particular proposal.
    """
    proposal = models.ForeignKey(Proposal, related_name="attributes")
    name = models.CharField(max_length=128)
    string_value = models.CharField(null=True, max_length=256)
    text_value = models.TextField(null=True)
    date_value = models.DateTimeField(null=True)

    def to_dict(self):
        return {"name": self.name,
                "value": self.string_value or \
                self.text_value or \
                self.date_value}

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

    # If available, determine when the document was published.
    published = models.DateTimeField(null=True)

    # If the document has been copied to the local filesystem:
    document = models.FileField(null=True)

    # File containing extracted text of the document:
    fulltext = models.FileField(null=True)
    encoding = models.CharField(max_length=20, default="")
    # File containing a thumbnail of the document:
    thumbnail = models.FileField(null=True)

    class Meta:
        # Ensure at the DB level that documents are not duplicated:
        unique_together = (("proposal", "url"))

    def get_absolute_url(self):
        return reverse("view-document", kwargs={"pk": self.pk})

    def to_dict(self):
        d = model_to_dict(self, exclude=["event", "document",
                                         "fulltext", "thumbnail"])
        if self.thumbnail:
            d["thumb"] = self.thumbnail.url

        if self.document:
            d["url"] = self.document.url

        return d

class Image(models.Model):
    """An image associated with a document. In the future, it may be
    worthwhile to alter this to allow images associated directly with a
    proposal.

    """
    proposal = models.ForeignKey(Proposal)
    document = models.ForeignKey(Document, null=True)
    image = models.FileField()
    thumbnail = models.FileField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("proposal", "image"))

    @property
    def url(self):
        return self.thumbnail and self.thumbnail.url or self.image.url
