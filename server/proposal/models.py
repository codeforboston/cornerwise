from datetime import datetime

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.db import IntegrityError
from django.db.models import Q
from django.forms.models import model_to_dict

import pickle
import pytz
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

    def for_parcel(self, parcel):
        return self.filter(location__within=parcel.shape)


def make_property_map():
    def _g(p):
        return lambda d: d.get(p, "")

    def _G(p):
        return lambda d: d[p]

    def get_other_addresses(d):
        return ";".join(d["all_addresses"][1:]) if "all_addresses" in d else ""

    return [("address", _G("address")),
            ("other_addresses", get_other_addresses),
            ("location", lambda d: Point(d["long"], d["lat"])),
            ("summary", lambda d: d.get("summary", "")[0:1024]),
            ("description", _g("description")), ("source", _g("source")),
            ("region_name", _g("region_name")),
            ("updated", _G("updated_date")), ("complete", _G("complete"))]


property_map = make_property_map()


class Proposal(models.Model):
    case_number = models.CharField(
        max_length=64,
        unique=True,
        help_text=("The unique case number "
                   "assigned by the city"))
    address = models.CharField(max_length=128, help_text="Street address")
    other_addresses = models.CharField(
        max_length=250,
        blank=True,
        help_text="Other addresses covered by this proposal")
    location = models.PointField(help_text="The latitude and longitude")
    region_name = models.CharField(
        max_length=128, default="Somerville, MA", null=True, help_text="")
    # The time when the proposal was last saved:
    modified = models.DateTimeField(auto_now=True)
    # The last time that the source was changed:
    updated = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    summary = models.CharField(max_length=1024, default="")
    description = models.TextField(default="")
    source = models.URLField(
        null=True, help_text="The data source for the proposal.")
    status = models.CharField(max_length=64)

    # A proposal can be associated with a Project:
    project = models.ForeignKey("project.Project", blank=True, null=True)
    # A misnomer; if True, indicates that the planning board has issued a
    # ruling (approval or disapproval):
    complete = models.BooleanField(default=False)

    parcel = models.ForeignKey(
        "parcel.Parcel", related_name="proposals", null=True, on_delete=models.SET_NULL)

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
                    prop_changes.append({
                        "name": p,
                        "new": val,
                        "old": old_val
                    })
                setattr(proposal, p, val)
            except Exception as exc:
                if old_val:
                    continue
                raise Exception("Missing required property: %s\n Reason: %s" %
                                (p, exc))

        proposal.save()

        proposal.create_events(p_dict.get("events"))

        # Create associated documents:
        proposal.create_documents((field, val["links"])
                                  for field, val in p_dict.items()
                                  if isinstance(val, dict) and val.get("links"))

        if changed:
            attr_changes = []
        for attr_name, attr_val in p_dict.get("attributes", []):
            try:
                handle = utils.normalize(attr_name)
                attr = proposal.attributes.get(handle=handle)
                old_val = attr.text_value
            except Attribute.DoesNotExist:
                proposal.attributes.create(
                    name=attr_name,
                    handle=handle,
                    text_value=attr_val,
                    published=p_dict["updated_date"])
                old_val = None
            if changed:
                attr_changes.append({
                    "name": attr_name,
                    "old": old_val,
                    "new": attr_val
                })

        if changed:
            changeset = Changeset.from_changes(proposal, {
                "properties": prop_changes,
                "attributes": attr_changes
            })
            changeset.save()

        return (created, proposal)

    def create_documents(self, docs):
        for field, links in docs:
            for link in links:
                try:
                    doc = proposal.document_set.get(url=link["url"])
                except Document.DoesNotExist:
                    doc = Document(proposal=proposal)

                    doc.url = link["url"]
                    doc.title = link["title"]
                    doc.field = field
                    doc.published = p_dict["updated_date"]

                    doc.save()

    def create_events(self, events_json):
        if events_json:
            for event_json in events_json:
                event_json["cases"] = [self.case_number]
                Event.make_event(event_json)


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

    # class Meta:
    #     unique_together = ("proposal", "handle")

    def to_dict(self):
        d = {"name": self.name, "handle": self.handle}
        if self.text_value:
            d["value"] = self.text_value
            d["value_type"] = "text"
        elif self.date_value:
            d["value"] = self.date_value.isoformat()
            d["value_type"] = "date"

        return d

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


class EventManager(models.Manager):
    def upcoming(self):
        today = pytz.UTC.localize(datetime.today())
        return self.filter(date__gte=today).order_by("date")


class Event(models.Model):
    """
    Meeting or hearing associated with a proposal.
    """
    title = models.CharField(max_length=256, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(db_index=True)
    duration = models.DurationField(null=True)
    location = models.CharField(
        max_length=256, default="Somerville City Hall, 93 Highland Ave")
    region_name = models.CharField(max_length=128, default="Somerville, MA")
    description = models.TextField()
    proposals = models.ManyToManyField(
        Proposal, related_name="events", related_query_name="event")
    minutes = models.URLField(blank=True)

    objects = EventManager()

    class Meta:
        unique_together = (("date", "title", "region_name"))

    def to_json_dict(self):
        d = model_to_dict(self, exclude=["created", "proposals"])
        return d

    @classmethod
    def make_event(cls, event_json):
        """
        event_json should have the following fields:
        - title (str) - Name of the event
        - description (str)
        - date (datetime with local timezone) - When will the event occur?
        - cases - A list of case numbers
        - region_name
        - duration (timedelta, optional) - how long will the event last?
        - agenda_url (string, optional)
        """
        keys = ("title", "description", "date", "region_name", "duration")
        try:
            event = cls.objects.get(title=event_json["title"],
                                    date=event_json["date"],
                                    region_name=event_json["region_name"])
            for k in keys:
                setattr(event, k, event_json.get(k))
            event.minutes = event_json.get("agenda_url")
        except cls.DoesNotExist:
            kwargs = {k: event_json.get(k) for k in keys}
            kwargs["minutes"] = event_json.get("agenda_url", "")
            event = cls(**kwargs)

        event.save()

        for case_number in event_json["cases"]:
            try:
                proposal = Proposal.objects.get(case_number=case_number)
                event.proposals.add(proposal)
            except Proposal.DoesNotExist:
                continue

        return event


def upload_document_to(doc, filename):
    return "doc/%s/%s" % (doc.pk, filename)


class Document(models.Model):
    """
    A document associated with a proposal.
    """
    proposal = models.ForeignKey(Proposal)
    event = models.ForeignKey(
        Event, null=True, help_text="Event associated with this document")
    url = models.URLField()
    title = models.CharField(
        max_length=256, help_text="The name of the document")
    field = models.CharField(
        max_length=256,
        help_text=("The field in which the document was found"))
    # Record when the document was first observed:
    created = models.DateTimeField(auto_now_add=True)

    # If available: when the document was published.
    published = models.DateTimeField(null=True)

    # If the document has been copied to the local filesystem:
    document = models.FileField(null=True, upload_to=upload_document_to)

    # File containing extracted text of the document:
    fulltext = models.FileField(null=True)
    encoding = models.CharField(max_length=20, default="")
    # File containing a thumbnail of the document:
    thumbnail = models.FileField(null=True, upload_to=upload_document_to)

    class Meta:
        # Ensure at the DB level that documents are not duplicated:
        unique_together = (("proposal", "url"))

    def get_absolute_url(self):
        return reverse("view-document", kwargs={"pk": self.pk})

    def to_dict(self):
        d = model_to_dict(
            self, exclude=["event", "document", "fulltext", "thumbnail"])
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


@receiver(models.signals.post_delete, sender=Document)
def auto_delete_document(**kwargs):
    document = kwargs["instance"]
    if document.document:
        document.document.delete(save=False)
    if document.thumbnail:
        document.thumbnail.delete(save=False)
    if document.fulltext:
        document.fulltext.delete(save=False)


def upload_image_to(doc, filename):
    fmt = "doc/%s/images/%s" if doc.document else "prop/%s/%s"
    return fmt % (doc.document_id, filename)


class Image(models.Model):
    """
    An image associated with a proposal and (optionally) with a document.
    """
    proposal = models.ForeignKey(Proposal, related_name="images")
    document = models.ForeignKey(
        Document, null=True, help_text="Source document for image")
    image = models.FileField(null=True, upload_to=upload_image_to)
    width = models.IntegerField()
    height = models.IntegerField()
    thumbnail = models.FileField(null=True)
    url = models.URLField(null=True, unique=True, max_length=512)
    # Crude way to specify that an image should not be copied to the
    # local filesystem:
    skip_cache = models.BooleanField(default=False)
    # Crude form of ranking. Images with lower priority values are shown first
    # in the UI.
    priority = models.IntegerField(default=0, db_index=True)
    source = models.CharField(max_length=64, default="document")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("proposal", "image"))

    def get_url(self):
        return self.image and self.image.url or self.url

    def to_dict(self):
        return {
            "id": self.pk,
            "src": self.get_url(),
            "thumb": self.thumbnail.url if self.thumbnail else None
        }


@receiver(models.signals.post_delete, sender=Image)
def auto_delete_image(**kwargs):
    image = kwargs["instance"]
    if image.image:
        image.image.delete(save=False)
    if image.thumbnail:
        image.thumbnail.delete(save=False)


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
