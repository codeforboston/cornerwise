from datetime import timedelta
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.gis.measure import D
from django.core.exceptions import ValidationError
from django import forms
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic.edit import FormView

import bleach
from tinymce.widgets import TinyMCE

from utils import read_n_from_end, Redis, lget_key, split_list
from shared.geocoder import geocode_tuples


from .admin import cornerwise_admin
from .widgets import DistanceField


is_superuser = user_passes_test(lambda user: user.is_superuser, "/admin")


def get_task_logs(task_ids):
    with Redis.pipeline() as p:
        for task_id in task_ids:
            p.lrange(f"cornerwise:task_log:{task_id}", 0, 100)
        logs = p.execute()

    return dict(zip(task_ids, [map(bytes.decode, reversed(l))
                               for l in logs]))


@is_superuser
def celery_logs(request):
    nlines = int(request.GET.get("n", "100"))
    with open("logs/celery_tasks.log", "rb") as log:
        log_lines = read_n_from_end(log, nlines)

    context = cornerwise_admin.each_context(request)
    context.update({"log_name": "Celery Tasks Log",
                    "lines": log_lines,
                    "title": "Task Logs"})
    return render(request, "admin/log_view.djhtml", context)


@is_superuser
def task_failure_logs(request):
    context = cornerwise_admin.each_context(request)
    context.update({"failures": lget_key("cornerwise:logs:task_failure"),
                    "title": "Recent Task Failures"})
    return render(request, "admin/task_failure_log.djhtml", context)


@is_superuser
def task_logs(request):
    task_ids = request.GET.getlist("task_id")
    context = cornerwise_admin.each_context(request)
    context.update({"logs": get_task_logs(task_ids),
                    "title": "Task Logs"})

    return render(request, "admin/task_logs.djhtml", context)


@is_superuser
def recent_tasks(request):
    """Displays a list of recently completed tasks."""
    n = request.GET.get("n", "100")
    n = max(10, min(1000, int(n)))
    recent_task_info = lget_key("cornerwise:recent_tasks", n)
    context = cornerwise_admin.each_context(request)
    context.update({"tasks": recent_task_info,
                    "title": "Recent Tasks"})
    return render(request, "admin/recent_tasks.djhtml", context)


# Send message to users
class UserNotificationFormView(FormView):
    """Form for sending messages to users near an address.

    """
    template_name = "admin/notify_users.djhtml"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(cornerwise_admin.each_context(self.request))
        context["title"] = "Send User Notifications"
        return context

    class form_class(forms.Form):
        addresses = forms.CharField(
            widget=forms.Textarea(attrs={"rows": 5}),
            help_text=("Enter one address per line"),
            required=False)
        proposals = forms.ModelMultipleChoiceField(queryset=None,
                                                   required=False)
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

        def __init__(self, *args, **kwargs):
            from proposal.models import Proposal

            super().__init__(*args, **kwargs)
            self.data = self.data.copy()
            self.fields["proposals"].queryset = Proposal.objects.filter(
                updated__gte=timezone.now() - timedelta(days=30),
                region_name=settings.GEO_REGION)

        def geocode_addresses(self, addresses):
            addresses = list(filter(None, map(str.strip, addresses)))
            geocoded = geocode_tuples(addresses,
                                      region=self.cleaned_data["region"])
            return split_list(tuple.__instancecheck__, geocoded)

        def clean(self):
            cleaned = super().clean()

            addresses = cleaned["addresses"].split("\n")
            good_addrs, bad_addrs = self.geocode_addresses(addresses)

            self.data["addresses"] = "\n".join(addr for addr, _pt, _fmt in
                                               good_addrs)

            if bad_addrs:
                raise ValidationError(("Not all addresses were validated: "
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

        def get_addresses(self):
            return "; ".join(f"{fmt_addr}: {pt.y}, {pt.x}" for _, pt, fmt_addr
                             in self.cleaned_data["coded_addresses"])

        def send_emails(self):
            data = self.cleaned_data
            address = data["address"]
            message = data["message"]
            return data["lat"], data["lng"], data["formatted_address"]

    def form_valid(self, form):
        # lat, lng, fmt = form.send_emails()
        addresses = form.get_addresses()
        messages.success(self.request, f"Found addresses: {addresses}")
        return redirect("/admin")


user_notification_form = is_superuser(UserNotificationFormView.as_view())
