from datetime import datetime

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.forms.models import model_to_dict

import pickle
import utils


class ProposalManager(models.GeoManager):
    def latest(self):
        results = self.order_by("-created")
        return results and results[0]

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

        return self.filter(q)

    def build_query(self, params):
        "Construct a query from parameters"
        pass

    def for_parcel(self, parcel):
        return self.filter(location__within=parcel.shape)


def make_property_map():
    def _g(p): lambda d: d.get(p, "")

    def _G(p): lambda d: d[p]

    [("address", _G("address")),
     ("location", lambda d: Point(d["long"], d["lat"])),
     ("summary", lambda d: d.get("summary", "")[0:1024]),
     ("description", _g("description")),
     ("source", _g("source")),
     ("region_name", _g("region_name")),
     ("updated", _G("updated_date")),
     ("complete", _G("complete"))]

property_map = make_property_map()


class Proposal(models.Model):
    case_number = models.CharField(max_length=64,
                                   unique=True,
                                   help_text=("The unique case number "
                                              "assigned by the city"))
    address = models.CharField(max_length=128,
                               help_text="Street address")
    location = models.PointField(help_text="The latitude and longitude")
    region_name = models.CharField(max_length=128,
                                   default="Somerville, MA",
                                   null=True,
                                   help_text="")
    # The time when the proposal was last saved:
    modified = models.DateTimeField(auto_now=True)
    # The last time that the source was changed:
    updated = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    summary = models.CharField(max_length=1024, default="")
    description = models.TextField(default="")
    source = models.URLField(null=True,
                             help_text="The data source for the proposal.")
    status = models.CharField(max_length=64)

    # A proposal can be associated with a Project:
    project = models.ForeignKey("project.Project", blank=True, null=True)
    # A misnomer; if True, indicates that the proposal has been approved:
    complete = models.BooleanField(default=False)

    # To enable geo queries
    objects = ProposalManager()

    def get_absolute_url(self):
        return reverse("view-proposal", kwargs={"pk": self.pk})

    def document_for_field(self, field):
        return self.document_set.filter(field=field)

    @classmethod
    def create_or_update_proposal_from_dict(kls, p_dict):
        """
        Constructs a Proposal from a dictionary.  If an existing proposal has a
        matching case number, update it from p_dict."""
        try:
            proposal = kls.objects.get(case_number=p_dict["case_number"])
            created = False
        except kls.DoesNotExist:
            proposal = kls(case_number=p_dict["case_number"])
            created = True

        changed = not created
        if changed:
            prop_changes = []

        for p, fn in property_map:
            old_val = changed and getattr(proposal, p)
            try:
                val = fn(p_dict)
                if changed and val != old_val:
                    prop_changes.push({"name": p,
                                       "new": val,
                                       "old": old_val})
                setattr(proposal, p, fn(p_dict))
            except:
                if old_val:
                    continue
                return (False, None)

        proposal.save()

        # Create associated documents:
        for field, val in p_dict.items():
            if not isinstance(val, dict) or not val.get("links"):
                continue

            for link in val["links"]:
                try:
                    doc = proposal.document_set.get(url=link["url"])
                except Document.DoesNotExist:
                    doc = Document(proposal=proposal)

                    doc.url = link["url"]
                    doc.title = link["title"]
                    doc.field = field
                    doc.published = p_dict["updated_date"]

                    doc.save()

        if changed:
            attr_changes = []
        for attr_name, attr_val in p_dict.get("attributes", []):
            try:
                handle = utils.normalize(attr_name)
                attr = proposal.attributes.get(handle=handle)
                old_val = attr.text_value
            except Attribute.DoesNotExist:
                proposal.attributes.create(name=attr_name,
                                           handle=handle,
                                           text_value=attr_val,
                                           published=p_dict["updated_date"])
                old_val = None
            if changed:
                attr_changes.push({"name": attr_name,
                                   "old": old_val,
                                   "new": attr_val})

        if changed:
            changeset = Changeset.from_changes(proposal,
                                               {"properties": prop_changes,
                                                "attributes": attr_changes})
            changeset.save()

        return (created, proposal)


class Attribute(models.Model):
    """
    Arbitrary attributes associated with a particular proposal.
    """
    proposal = models.ForeignKey(Proposal, related_name="attributes")
    name = models.CharField(max_length=128)
    handle = models.CharField(max_length=128, db_index=True,
                              unique=True)

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

    def save(self):
        super(Attribute, self).save()
        # Update the stamp on the related proposal
        self.proposal.save()


class Event(models.Model):
    """
    Meeting or hearing associated with a proposal.
    """
    title = models.CharField(max_length=256, db_index=True)
    date = models.DateTimeField(db_index=True)
    duration = models.DurationField(null=True)
    description = models.TextField()
    proposals = models.ManyToManyField(Proposal, related_name="proposals")

    def to_dict(self):
        return model_to_dict(self, exclude=["proposals"])


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
                             help_text=("The field in which the document"
                                        " was found"))
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
        return {"id": self.pk,
                "src": self.get_url(),
                "thumb": self.thumbnail.url if self.thumbnail else None}


class Changeset(models.Model):
    """
    Model used to record the changes to a Proposal over time.
    """
    proposal = models.ForeignKey(Proposal, related_name="changes")
    created = models.DateTimeField(auto_now_add=True)
    change_blob = models.BinaryField()

    @classmethod
    def from_changes(kls, proposal, changes):
        instance = kls(proposal=proposal)
        instance.changes = changes
        return instance

    @property
    def changes(self):
        # { "properties": [ { } ] ,
        #   "attributes": [ { } ] }
        d = getattr(self, "_change_dict", None)
        if not d:
            d = pickle.loads(self.change_blob) if self.change_blob else {}
            self._change_dict = d
        return d

    @changes.setter
    def changes(self, d):
        self._change_dict = d
        self.change_blob = pickle.dumps(d)
