from datetime import timedelta

from django.contrib.auth.decorators import (permission_required,
                                            user_passes_test)
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from celery.task import control

import redis_utils as red
from utils import read_n_from_end

from proposal.models import Importer, Proposal
from proposal.tasks import add_parcel

from .admin import cornerwise_admin


is_superuser = user_passes_test(lambda user: user.is_superuser, "/admin")
can_view_logs = permission_required("shared.view_debug_logs", login_url="admin:login")


def get_task_logs(task_ids):
    with red.Redis.pipeline() as p:
        for task_id in task_ids:
            p.lrange(f"cornerwise:task_log:{task_id}", 0, 100)
        logs = p.execute()

    return dict(zip(task_ids, [map(bytes.decode, reversed(l))
                               for l in logs]))


@can_view_logs
def celery_logs(request):
    nlines = int(request.GET.get("n", "100"))
    with open("logs/celery_tasks.log", "rb") as log:
        log_lines = map(bytes.decode, read_n_from_end(log, nlines))

    context = cornerwise_admin.each_context(request)
    context.update({"log_name": "Celery Tasks Log",
                    "lines": log_lines,
                    "options": [100, 500, 1000],
                    "selected": nlines,
                    "title": "Celery Logs"})
    return render(request, "admin/log_view.djhtml", context)


@can_view_logs
def task_failure_logs(request):
    context = cornerwise_admin.each_context(request)
    context.update({"failures": red.lget_key("cornerwise:logs:task_failure"),
                    "title": "Recent Task Failures"})
    return render(request, "admin/task_failure_log.djhtml", context)


@can_view_logs
def task_logs(request):
    task_ids = request.GET.getlist("task_id")
    context = cornerwise_admin.each_context(request)
    context.update({"logs": get_task_logs(task_ids),
                    "title": "Task Logs"})

    return render(request, "admin/task_logs.djhtml", context)


@can_view_logs
def recent_tasks(request):
    """Displays a list of recently completed tasks."""
    n = request.GET.get("n", "100")
    n = max(10, min(1000, int(n)))
    recent_task_info = red.lget_key("cornerwise:recent_tasks", n)
    context = cornerwise_admin.each_context(request)
    context.update({"tasks": recent_task_info,
                    "title": "Recent Tasks"})
    return render(request, "admin/recent_tasks.djhtml", context)


def uptime_to_date(seconds):
    return timezone.now() - timedelta(seconds=seconds)


@can_view_logs
def task_stats(request):
    celery_inspect = control.inspect()
    stats = celery_inspect.stats()
    active = celery_inspect.active()
    scheduled = celery_inspect.scheduled()

    context = cornerwise_admin.each_context(request)
    context.update({"nodes": {node: {"tasks": nodestats["total"],
                                     "active": active[node],
                                     "scheduled": scheduled[node],
                                     "up_since": uptime_to_date(int(nodestats["clock"]))}
                              for node, nodestats in (stats.items() if stats else [])},
                    "title": "Celery Stats"})

    return render(request, "admin/task_stats.djhtml", context)


@is_superuser
@require_POST
def refresh_parcels(request):
    unmatched = Proposal.objects.filter(parcel=None)
    count = sum(bool(add_parcel(p)) for p in unmatched)
    messages.success(request,
                     f"Found matching parcel(s) for {count} proposal(s)")
    return redirect("admin:index")


@is_superuser
def importer_errors(request):
    context = cornerwise_admin.each_context(request)
    context.update({"importers": [
        {"importer": importer,
         "errors": red.lget_key(f"cornerwise:importer:{importer.pk}:import_errors")}
        for importer in Importer.objects.filter(pk__in=request.GET.getlist("importer"))
    ],
                    "title": "Importer Errors"})
    return render(request, "admin/importer_errors.djhtml", context)
