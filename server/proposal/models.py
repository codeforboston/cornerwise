import os, redis
from datetime import datetime

from django.conf import settings
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.models import model_to_dict

import utils

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
    summary = models.CharField(max_length=256, default="")
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
    handle = models.CharField(max_length=128, db_index=True)

    # Either the date when the source document was published or the date
    # when the attribute was observed:
    published = models.DateTimeField()
    text_value = models.TextField(null=True)
    date_value = models.DateTimeField(null=True)

    def to_dict(self):
        return {"name": self.name,
                "handle": self.handle,
                "value": self.text_value or self.date_value}

    def set_value(self, v):
        if isinstance(v, str):
            self.text_value = v
        elif isinstance(v, datetime):
            self.date_value = v

    def clear_value(self):
        self.text_value = None
        self.date_value = None

    @property
    def value(self):
        return self.text_value or \
            self.date_value


class Event(models.Model):
    """
    Meeting or hearing associated with a proposal.
    """
    title = models.CharField(max_length=256, db_index=True)
    date = models.DateTimeField(db_index=True)
    duration = models.DurationField(null=True)
    description = models.TextField()
    proposals = models.ManyToManyField(Proposal, related_name="proposals")


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

    # If available: when the document was published.
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

    def get_text(self):
        with open(self.fulltext.path, "r", encoding=self.encoding) as f:
            return f.read()

    @property
    def local_path(self):
        return self.document and self.document.path or ""

    move_file = utils.make_file_mover("document")


class Image(models.Model):
    """An image associated with a document.
    """
    proposal = models.ForeignKey(Proposal, related_name="images")
    document = models.ForeignKey(Document, null=True,
                                 help_text="Source document for image")
    image = models.FileField(null=True)
    thumbnail = models.FileField(null=True)
    url = models.URLField(null=True, unique=True)
    # Crude way to specify that an image should not be copied to the
    # local filesystem:
    skip_cache = models.BooleanField(default=False)
    priority = models.IntegerField(default=0, db_index=True)
    source = models.CharField(max_length=64, default="document")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("proposal", "image"))

    def get_url(self):
        return self.image and self.image.url or self.url

    def to_dict(self):
        return {"src": self.get_url(),
                "thumb": self.thumbnail.url if self.thumbnail else None}
