from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.exceptions import ValidationError
from django import forms
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView

from utils import read_n_from_end, Redis, lget_key
from shared.geocoder import Geocoder

from .admin import cornerwise_admin


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
    context.update({"tasks": recent_task_info})
    return render(request, "admin/recent_tasks.djhtml", context)


# Send message to users
class UserNotificationFormView(FormView):
    """Form for sending messages to users near an address.

    """
    template_name = "admin/notify_users.djhtml"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(cornerwise_admin.each_context(self.request))
        return context

    class form_class(forms.Form):
        address = forms.CharField(label="Address")
        message = forms.CharField(widget=forms.Textarea())
        region = forms.ChoiceField(choices=(("Somerville, MA", "Somerville, MA"),))

        def clean(self):
            cleaned = super().clean()
            address = cleaned["address"]
            region = cleaned["region"]
            [result] = Geocoder.geocode([f"{address}, {region}"])
            if not result:
                raise ValidationError(
                    f"Lookup for address failed: {address}.\n"
                    f"Please enter a valid street address in {region}.")
            cleaned["lat"] = result["location"]["lat"]
            cleaned["lng"] = result["location"]["lng"]
            cleaned["formatted_address"] = result["formatted_name"]
            return cleaned

        def send_emails(self):
            data = self.cleaned_data
            address = data["address"]
            message = data["message"]
            return data["lat"], data["lng"], data["formatted_address"]

    def form_valid(self, form):
        lat, lng, fmt = form.send_emails()
        messages.success(self.request, f"Found address: {lat}, {lng} ({fmt})")
        return redirect("/admin")


user_notification_form = is_superuser(UserNotificationFormView.as_view())
