import urllib
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.measure import D
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import F, Q
from django.urls import reverse
from django.utils import timezone

from utils import bounds_from_box, distance_from_str, point_from_str, prettify_lat, prettify_long
from .changes import summarize_subscription_updates
from site_config import site_config

from base64 import b64encode
from datetime import datetime
import os
import pickle


def make_token():
    """
    :returns: (str) an authentication token
    """
    return b64encode(os.urandom(32)).decode("utf-8")


def prettify_point(pt):
    return prettify_lat(pt.y) + ", " + prettify_long(pt.x)


def poly_bounds(poly):
    bounds = poly.envelope.tuple[0]
    return bounds[2], bounds[0]


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

    def find_similar(self, subscription):
        for sub in self:
            if sub.pk == subscription.pk:
                continue
            yield (self.similarity(sub), sub)

    def most_similar(self, subscription):
        max_similarity = 0
        match = None
        for (sim, sub) in self.find_similar(subscription):
            if sub.pk != subscription.pk and sim >= max_similarity:
                match = sub
                max_similarity = sim
        return (max_similarity, match)


class Subscription(models.Model):
    """A Subscription contains a saved query. Cornerwise checks it for updates
    every few days and sends the user a digest

    """
    # The subscription belongs to a registered user:
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
    address = models.CharField(max_length=64, blank=True,
                               help_text="Optional address for the center point")
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

    def confirm(self):
        """Activate this subscription. If multiple subscriptions are disallowed,
        deactivate the user's currently active subscriptions.

        """
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
        """Ensures that the query, a dict, is well-formed and valid.

        """
        if "box" in q:
            self.box = bounds_from_box(q["box"])
        elif "center" in q:
            if "r" in q:
                self.center = point_from_str(q["center"])
                self.radius = distance_from_str(q["r"]).m
            else:
                raise ValidationError(f"Missing query parameter: r")
        if "region_name" in q:
            self.region_name = q["region_name"]

        q = self.validate_site_settings(q)

        self.query = pickle.dumps(q)

    def validate_site_settings(self, q):
        """If the Subscription has an associated site name, perform additional
        validation of the subscription params according to the specific rules
        for that site. Called after the properties have been successfully
        deserialized and set.

        """
        if not self.site_name:
            return q

        config = site_config(self.site_name)

        return config.validate_subscription_query(self, q)

    @staticmethod
    def readable_query(query, unit="ft"):
        # NOTE Not currently used, but may be useful again in the future
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
            box = bounds_from_box(query["box"])
            sw, ne = poly_bounds(box)
            desc += "".join(["inside the region: ",
                             prettify_point(sw), " and ", prettify_point(ne)])
        elif "center" in query:
            dist = D(m=query["r"])

        return desc

    def readable_description(self, dist_units="ft"):
        """Returns a brief textual description of the subscription.

        """
        desc = "projects "
        if self.box:
            sw, ne = poly_bounds(self.box)
            desc += f"inside the region: {prettify_point(sw)} and {prettify_point(ne)}"
        elif self.center:
            dist = round(getattr(D(m=self.radius), dist_units))
            desc += "within {dist} {dist_units} of {where}".format(
                dist=dist,
                dist_units=dist_units,
                where=(self.address or prettify_point(self.center))
            )

        desc += f" ({self.region_name})"

        return desc

    def overlap(self, subscription):
        """Returns the overlap of the subscription area of this Subscription with
        another Subscription as a percentage of the total area of the two
        subscriptions. If only one of the subscriptions has a shape, returns 0.
        If neither has a shape, returns None.

        """
        my_shape = self.shape
        other_shape = subscription.shape

        if my_shape and other_shape:
            return 2*my_shape.intersection(other_shape).area/(my_shape.area + other_shape.area)
        elif my_shape or other_shape:
            return 0

        return None

    def similarity(self, subscription):
        if self.region_name != subscription.region_name:
            return 0

        # Be sure to add other fields as necessary

        overlap = self.overlap(subscription)
        if overlap is not None:
            return overlap

        if self.address == subscription.address:
            return 1

    @property
    def map_url(self):
        """Creates a link to the main map page with the center of the map set to the
        center of the subscription.

        """
        center = self.center or self.box.centroid
        params = urllib.parse.urlencode({
            "view": "main",
            "lat": center.y,
            "lng": center.x,
            "zoom": 17,
            "ref.lat": center.y,
            "ref.lng": center.x,
            "ref.r": self.radius,
            "ref.address": self.address,
        }, quote_via=urllib.parse.quote)
        return reverse("front-page") + "#" + params

    @property
    def shape(self):
        if self.box:
            return self.box
        else:
            center = self.center
            # This is good enough for our purposes here:
            return center.buffer(self.radius/111000)

    def minimap_src(self, circle_color=None):
        box = self.shape

        if box:
            sw, ne = poly_bounds(box)

            circle = f"{int(self.radius)}" if self.radius else ""
            if circle_color and self.radius:
                circle += f",{circle_color}"
            return settings.MINIMAP_SRC\
                .format(swlat=sw[1], swlon=sw[0],
                        nelat=ne[1], nelon=ne[0],
                        circle=circle)
        else:
            return None


class UserComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True)
    created = models.DateTimeField(default=timezone.now)
    subject = models.CharField(max_length=100)
    send_to = models.CharField(max_length=100)
    comment = models.CharField(max_length=1000)
    remote_addr = models.GenericIPAddressField()
    remote_host = models.CharField(max_length=100)
    site_name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.user}: {self.subject}"
