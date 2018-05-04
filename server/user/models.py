import urllib
from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import F, Q
from django.urls import reverse
from django.utils import timezone

from utils import bounds_from_box, point_from_str, prettify_lat, prettify_long
from .changes import summarize_subscription_updates

from base64 import b64encode
from datetime import datetime
import os
import pickle


def make_token():
    """
    :returns: (str) an authentication token
    """
    return b64encode(os.urandom(32))


class UserProfile(models.Model):
    """
    Extension to the built-in User class that adds a token for allowing
    password-less login from email links.

    For now, we can get away with this, because we won't be handling any
    sensitive data.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name="profile")
    token = models.CharField(max_length=64, default=make_token)
    language = models.CharField(max_length=10, default="en")
    nickname = models.CharField(max_length=128,
                                help_text="What do you prefer to be called?")
    site_name = models.CharField(
        help_text="The site where the user created his/her account",
        db_index=True,
        max_length=64,
        default="somerville.cornerwise.org")

    @property
    def addressal(self):
        return self.nickname or self.user.first_name

    def activate(self):
        """Activates a user account.
        """
        if not self.user.is_active:
            self.user.is_active = True
            self.token = make_token()
            self.user.save()
            self.save()

    def deactivate(self):
        if not self.user.is_active:
            return

        self.user.is_active = False
        self.token = make_token()
        self.user.save()
        self.save()

        self.deactivate_subscriptions()

    def deactivate_subscriptions(self):
        self.user.subscriptions.update(active=False)

    def generate_token(self):
        "Creates a new verification token for the user and saves it."
        self.token = make_token()
        self.save()

        return self.token

    def url(self, url):
        return "{base}?token={token}&uid={uid}".format(
            base=url,
            token=urllib.parse.quote_plus(self.token),
            uid=self.user_id)

    @property
    def unsubscribe_url(self):
        return self.url(reverse("deactivate-account"))

    @property
    def manage_url(self):
        return self.url(reverse("manage-user"))

    @property
    def confirm_url(self):
        return self.url(reverse("confirm"))


class SubscriptionQuerySet(models.QuerySet):
    def containing(self, point):
        """
        Find Subscriptions whose notification area includes the point
        """
        return self.filter(Q(center__distance_lte=(point, F("radius"))) |
                           Q(box__contains=point))

    def in_radius(self, point, radius):
        return self.filter(Q(center__distance_lte=(point, radius)))

    def mark_sent(self):
        """Mark that the Subscriptions in the query set have been sent emails.

        """
        return self.update(last_notified=timezone.now())


class Subscription(models.Model):
    # The subscription belong to a registered user:
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="subscriptions",
                             on_delete=models.CASCADE)
    active = models.BooleanField(
        default=False,
        help_text="Users only receive updates for active subscriptions")
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    # Stores the pickle serialization of a dictionary describing the query
    query = models.BinaryField()
    center = models.PointField(
        help_text=("Center point of the query. Along with the radius, "
                   "determines the notification region."),
        geography=True,
        null=True)
    radius = models.FloatField(
        help_text="Radius in meters",
        db_index=True,
        validators=[MinValueValidator(settings.MIN_ALERT_RADIUS),
                    MaxValueValidator(settings.MAX_ALERT_RADIUS)],
        null=True)
    box = models.PolygonField(
        help_text=("The notification region. Either this or the center and "
                   "radius should be set."),
        db_index=True,
        null=True)
    region_name = models.CharField(
        help_text="Only subscribe to updates in this region",
        db_index=True,
        max_length=128,
        null=True)
    site_name = models.CharField(
        help_text="The site where the user created his/her account",
        db_index=True,
        max_length=64,
        default="somerville.cornerwise.org")

    # Implementation of text search requires more design work
    # text_search = models.CharField(
    #     max_length=1000,
    #     help_text="")
    include_events = models.CharField(
        max_length=256, default="", blank=True,
        help_text="Include events for a specified region")
    last_notified = models.DateTimeField(default=timezone.now)

    objects = SubscriptionQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super().save(*args, **kwargs)

    def clean(self):
        if bool(self.center) != bool(self.radius):  # nxor
            raise ValidationError("center and radius must be set together",
                                  params=["center", "radius"])
        if not (self.center or self.box):
            raise ValidationError("must have either a circle or box set",
                                  params=["center", "radius"])

        # TODO: If there's an associated region, check that the center lies
        # inside its bounds, if known.

    def confirm(self):
        if settings.LIMIT_SUBSCRIPTIONS:
            # Disable all this user's other subscriptions:
            self.user.subscriptions\
                     .filter(active=True)\
                     .exclude(pk=self.pk)\
                     .update(active=False)
        self.user.profile.activate()
        self.active = True
        self.save()

    def summarize_updates(self, since=None):
        """
        since: a datetime

        :returns: a dictionary describing the changes to the query since the
        given datetime
        """
        return summarize_subscription_updates(self, since or self.last_notified)

    @property
    def confirm_url(self):
        return "{base}?token={token}&uid={uid}&sub={sub_id}".format(
            base=reverse("confirm"),
            token=self.user.profile.token,
            uid=self.user.pk,
            sub_id=self.pk)

    @property
    def query_dict(self):
        q = {}
        if self.box:
            q["box"] = self.box
        if self.center:
            q["center"] = self.center
            q["r"] = self.radius
        if self.region_name:
            q["region_name"] = self.region_name
        return q

    def set_validated_query(self, q):
        if "box" in q:
            self.box = bounds_from_box(q["box"])
        elif "center" in q:
            if "r" in q:
                self.center = point_from_str(q["center"])
                self.radius = float(q["r"])
        if "region_name" in q:
            self.region_name = q["region_name"]

        self.query = pickle.dumps(q)

    @staticmethod
    def readable_query(query):
        if "projects" in query:
            if query["project"] == "all":
                desc = "Public proposals "
            else:
                desc = "Private proposals "
        else:
            desc = "All proposals "

        if "text" in query:
            desc += "matching \"" + query["text"] + "\" "

        if "box" in query:
            coords = [float(s) for s in query["box"].split(",")]
            desc += "".join(["inside the region: ",
                             prettify_lat(coords[0]), ", ",
                             prettify_long(coords[1]), " and ",
                             prettify_lat(coords[2]), ", ",
                             prettify_long(coords[3])])

        return desc

    @property
    def readable_description(self):
        return self.readable_query(self.query_dict)

    @property
    def minimap_src(self):
        if self.box:
            box = self.box
        else:
            center = self.center
            # This is good enough for our purposes here:
            box = center.buffer(self.radius/111000)

        if box:
            bounds = box.envelope.tuple[0]
            sw = bounds[2]
            ne = bounds[0]
            return settings.MINIMAP_SRC\
                .format(swlat=sw[1], swlon=sw[0], nelat=ne[1], nelon=ne[0])
        else:
            return None
