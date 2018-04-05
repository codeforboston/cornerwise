from collections import defaultdict, namedtuple
from itertools import chain
import re
from uuid import uuid4
from urllib.parse import urljoin

from django import forms
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from django.contrib import messages
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.contrib.auth.decorators import permission_required
from django.contrib.gis.measure import D
from django.core.exceptions import ValidationError

import bleach
from tinymce.widgets import TinyMCE

import redis_utils as red
from utils import split_list
from shared.geocoder import geocode_tuples

from proposal.models import Proposal
from user.models import Subscription

from .admin import cornerwise_admin
from .widgets import DistanceField


can_send_notifications = permission_required("shared.send_notifications")


def get_subscribers(geocoded=[], proposals=[],
                    region=settings.GEO_REGION,
                    notify_radius=D(ft=300)):
    """Get the Subscriptions that should be informed about the given geocoded
    addresses and/or proposals. Returns a dictionary of Subscriptions to
    (address/proposal, Point).

    :param geocoded: a list of tuples (address, Point, formatted_address)
    :param proposals: a list of Proposals

    """
    if not isinstance(notify_radius, D):
        notify_radius = D(ft=notify_radius)

    def coords(x):
        return x.location if isinstance(x, Proposal) else x[1]

    sub_near = defaultdict(list)
    for thing in chain(proposals, geocoded):
        point = coords(thing)
        if notify_radius:
            subs = Subscription.objects.filter(
                center__distance_lte=(point, notify_radius))
        else:
            subs = Subscription.objects.containing(point)

        for sub in subs:
            sub_near[sub].append((thing, coords))

    return sub_near


def template_replace(message, subs):
    return re.sub(r"%([a-z]+)%",
                  lambda m: subs.get(m.group(1), m.group(0)),
                  message)


def replace_boilerplate(message, related, region_name):
    proposals, addresses = split_list(lambda x: isinstance(x, Proposal),
                                      related)

    return template_replace(message, {
        "region": region_name,
        "proposals": "\n<br/>".join(f"{p.address} ({p.case_number})"
                                    for p in proposals),
        "addresses": "\n<br/>".join(addr[0] for addr in addresses)
    }).replace("\n", "\n<br/>")


RelModel = namedtuple("RelModel", ["model"])


def notification_key(nid):
    return f"cornerwise:notification:{nid}"


# Send message to users
class UserNotificationForm(forms.Form):
    """Create a new message to send to users in the vicinity of given proposals
    and/or addresses.

    """
    addresses = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text=("Enter one address per line"),
        required=False)
    proposals = forms.ModelMultipleChoiceField(
        queryset=Proposal.objects.all(),
        required=False,
        widget=AutocompleteSelectMultiple(RelModel(Proposal), cornerwise_admin,))
    greeting = forms.CharField(
        initial=("You are receiving this message from the "
                 "planning staff in %region% because you "
                 "have subscribed to receive emails about "
                 "development in your area. The affected "
                 "addresses in your area are:\n%proposals%\n"
                 "%addresses%"),
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text=("Use %region% to insert the region name, "
                   "<proposals> to insert a list of proposal "
                   "addresses and case numbers and %addresses% "
                   "to insert a list of addresses relevant to "
                   "the email recipient"))
    message = forms.CharField(
        widget=TinyMCE(mce_attrs={"width": 400, "height": 250,
                                  "content_css": urljoin(settings.STATIC_URL,
                                                         "css/tinymce.css")}))
    notification_radius = DistanceField(
        min_value=D(ft=100), max_value=D(mi=20), initial=D(ft=300),
        label="Notify subscribers within distance")
    # include_boilerplate = forms.BooleanField(
    #     initial=True, help_text=("Before sending the email to each user, "
    #                              "add a brief message listing the "
    #                              "address(es) or proposal(s) relevant to "
    #                              "that subscription"))
    region = forms.ChoiceField(choices=(("Somerville, MA", "Somerville, MA"),),
                               initial=settings.GEO_REGION)
    notification_id = forms.CharField(required=False,
                                      widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.data.copy()
        self.fields["notification_id"].initial = str(uuid4())

    @property
    def confirmed(self):
        return self.cleaned_data["confirm"]

    def mark_confirm(self):
        self.data["confirm"] = "1"

    def geocode_addresses(self, addresses):
        addresses = list(filter(None, map(str.strip, addresses)))
        geocoded = geocode_tuples(addresses,
                                  region=self.cleaned_data["region"])
        return split_list(tuple.__instancecheck__, geocoded)

    def find_matching_proposals(self, region):
        proposals = self.cleaned_data["proposals"]

        return split_list(lambda p: p.region_name == region,
                          proposals)

    def clean(self):
        cleaned = super().clean()

        # Check that the Proposals are within the selected region
        region = cleaned["region"]
        if region:
            good_props, bad_props = self.find_matching_proposals(region)
            if bad_props:
                self.data.setlist("proposals", [p.id for p in good_props])
                raise ValidationError(
                    (f"{len(bad_props)} proposal(s) are outside {region}."))

        addresses = cleaned["addresses"].split("\n")
        good_addrs, bad_addrs = self.geocode_addresses(addresses)

        # Remove bad addresses, so that they don't show up when the form is
        # redisplayed.
        self.data["addresses"] = "\n".join(addr for addr, _pt, _fmt in
                                           good_addrs)

        if bad_addrs:
            raise ValidationError(("Not all addresses were valid: "
                                   "%(addresses)s"),
                                  params={"addresses": ";".join(bad_addrs)})

        if not (good_addrs or cleaned["proposals"]):
            raise ValidationError(
                "Please provide at least one address or proposal")

        cleaned["coded_addresses"] = good_addrs

        return cleaned

    def clean_message(self):
        message = self.cleaned_data["message"]
        return bleach.clean(
            message,
            tags=bleach.ALLOWED_TAGS + ["p", "pre", "span", "h1", "h2",
                                        "h3", "h4", "h5", "h6"],
            attributes=["title", "href", "style"],
            styles=["text-decoration", "text-align"])

    def clean_notification_id(self):
        nid = self.cleaned_data["notification_id"]
        if nid and re.match(r"[0-9a-f]{32}$", nid, re.I):
            return nid
        else:
            return str(uuid4())

    def save_data(self):
        notification_id = self.cleaned_data["notification_id"]

        red.set_expire_key(notification_key(notification_id),
                           {"cleaned": self.cleaned_data,
                            "data": self.data},
                           ttl=3600)
        return notification_id

    def get_subscribers(self):
        d = self.cleaned_data
        return get_subscribers(d["coded_addresses"],
                               d["proposals"], d["region"],
                               d["notification_radius"])

    def example_greeting(self):
        return replace_boilerplate(
            self.cleaned_data["greeting"],
            chain(self.cleaned_data["proposals"],
                  self.cleaned_data["coded_addresses"]),
            self.cleaned_data["region"])


@can_send_notifications
def user_notification_form(request, form_data=None):
    context = cornerwise_admin.each_context(request).copy()

    if not form_data and request.method == "POST":
        form = UserNotificationForm(request.POST)
        context["title"] = "Review Notification"
        context["form"] = form
        if form.is_valid():
            subscribers = form.get_subscribers()
            context.update(form.cleaned_data)
            context.update({"subscribers": subscribers,
                            "recipient_count": len(subscribers),
                            "total_address_count": (len(form.cleaned_data["coded_addresses"]) + len(form.cleaned_data["proposals"])),
                            "example_greeting": form.example_greeting(),
                            "notification_id": form.save_data()})

            return render(request, "admin/review_notification.djhtml",
                          context)
    else:
        context["form"] = UserNotificationForm(form_data)

    context["title"] = "Send User Notifications"

    return render(request, "admin/notify_users.djhtml",
                  context)


@require_POST
def send_user_notification(request):
    notification_id = request.POST["notification_id"]
    # TODO: Handle localized button text
    go_back = request.POST.get("submit") == "Back"

    if go_back:
        saved = red.get_key(notification_key(notification_id))
    else:
        saved = red.get_and_delete_key(notification_key(notification_id))

    if not saved:
        messages.error(
            request,
            "Something went wrong, and the message could not "
            "be sent.")
        return redirect("notification_form")

    if go_back:
        return user_notification_form(request, saved["data"])

    # Otherwise, send it!
