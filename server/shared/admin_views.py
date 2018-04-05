from collections import defaultdict, namedtuple
from datetime import timedelta
from itertools import chain
import re
from uuid import uuid4
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.contrib.auth.decorators import (permission_required,
                                            user_passes_test)
from django.contrib import messages
from django.contrib.gis.measure import D
from django.core.exceptions import ValidationError
from django import forms
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

import bleach
from tinymce.widgets import TinyMCE

import redis_utils as red
from utils import split_list
from shared.geocoder import geocode_tuples

from proposal.models import Proposal
from user.models import Subscription

from .admin import cornerwise_admin
from .widgets import DistanceField


is_superuser = user_passes_test(lambda user: user.is_superuser, "/admin")
can_send_notifications = permission_required("shared.send_notifications")


def get_task_logs(task_ids):
    with red.Redis.pipeline() as p:
        for task_id in task_ids:
            p.lrange(f"cornerwise:task_log:{task_id}", 0, 100)
        logs = p.execute()

    return dict(zip(task_ids, [map(bytes.decode, reversed(l))
                               for l in logs]))


@permission_required("shared.view_debug_logs")
def celery_logs(request):
    nlines = int(request.GET.get("n", "100"))
    with open("logs/celery_tasks.log", "rb") as log:
        log_lines = red.read_n_from_end(log, nlines)

    context = cornerwise_admin.each_context(request)
    context.update({"log_name": "Celery Tasks Log",
                    "lines": log_lines,
                    "title": "Task Logs"})
    return render(request, "admin/log_view.djhtml", context)


@permission_required("shared.view_debug_logs")
def task_failure_logs(request):
    context = cornerwise_admin.each_context(request)
    context.update({"failures": red.lget_key("cornerwise:logs:task_failure"),
                    "title": "Recent Task Failures"})
    return render(request, "admin/task_failure_log.djhtml", context)


@permission_required("shared.view_debug_logs")
def task_logs(request):
    task_ids = request.GET.getlist("task_id")
    context = cornerwise_admin.each_context(request)
    context.update({"logs": get_task_logs(task_ids),
                    "title": "Task Logs"})

    return render(request, "admin/task_logs.djhtml", context)


@permission_required("shared.view_debug_logs")
def recent_tasks(request):
    """Displays a list of recently completed tasks."""
    n = request.GET.get("n", "100")
    n = max(10, min(1000, int(n)))
    recent_task_info = red.lget_key("cornerwise:recent_tasks", n)
    context = cornerwise_admin.each_context(request)
    context.update({"tasks": recent_task_info,
                    "title": "Recent Tasks"})
    return render(request, "admin/recent_tasks.djhtml", context)


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

    prop_coords = ((p, p.location, p.address) for p in proposals)

    sub_near = defaultdict(list)
    for thing, coords, address in chain(prop_coords, geocoded):
        if notify_radius:
            subs = Subscription.objects.filter(
                center__distance_lte=(coords, notify_radius))
        else:
            subs = Subscription.objects.containing(coords)

        for sub in subs:
            sub_near[sub].append((thing, coords))

    return sub_near


RelModel = namedtuple("RelModel", ["model"])


# Send message to users
class UserNotificationForm(forms.Form):
    """Create a new message to send to users in the vicinity of given proposals
    and/or addresses.

    """
    addresses = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5}),
        help_text=("Enter one address per line"),
        required=False)
    proposals = forms.ModelMultipleChoiceField(
        queryset=Proposal.objects.all(),
        required=False,
        widget=AutocompleteSelectMultiple(RelModel(Proposal), cornerwise_admin,))
    message = forms.CharField(widget=TinyMCE(
        mce_attrs={"width": 400, "height": 250,
                   "content_css": urljoin(settings.STATIC_URL,
                                          "css/tinymce.css")}))
    notification_radius = DistanceField(
        min_value=D(ft=100), max_value=D(mi=20), initial=D(ft=300),
        label="Notify subscribers within distance")
    include_boilerplate = forms.BooleanField(
        initial=True, help_text=("Before sending the email to each user, "
                                 "add a brief message listing the "
                                 "address(es) or proposal(s) relevant to "
                                 "that subscription"))
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

        red.set_expire_key(f"notification.{notification_id}",
                           {"cleaned": self.cleaned_data,
                            "data": self.data},
                           ttl=3600)
        return notification_id

    def get_subscribers(self):
        data = self.cleaned_data
        return get_subscribers(data["coded_addresses"],
                               data["proposals"], data["region"],
                               data["notification_radius"])


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
    key = f"notification.{notification_id}"

    if go_back:
        saved = red.get_key(key)
    else:
        saved = red.get_and_delete_key(key)

    if not saved:
        messages.error(
            "Something went wrong, and the message could not "
            "be sent.")
        return redirect("notification_form")

    if go_back:
        return user_notification_form(request, saved["data"])

    # Otherwise, send it!
