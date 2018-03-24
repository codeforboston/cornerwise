from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.exceptions import ValidationError
from django import forms
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView

from utils import read_n_from_end, Redis
from shared.geocoder import Geocoder


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

    return render(request, "admin/log_view.djhtml",
                  {"log_name": "Celery Tasks Log",
                   "lines": log_lines})


@is_superuser
def task_logs(request):
    task_ids = request.GET.getlist("task_id")
    return render(request, "admin/task_logs.djhtml",
                  {"logs": get_task_logs(task_ids)})


@is_superuser
def recent_tasks(request):
    """Displays a list of recently completed tasks."""
    n = request.GET.get("n", "100")
    n = max(10, min(1000, int(n)))
    recent_task_info = Redis.lrange("cornerwise:recent_tasks", 0, n)
    return render(request, "admin/recent_tasks.djhtml",
                  {"tasks": recent_task_info})


# Send message to users
class UserNotificationFormView(FormView):
    """Form for sending messages to users near an address.

    """
    template_name = "admin/notify_users.djhtml"

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
