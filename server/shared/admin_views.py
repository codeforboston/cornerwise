from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from utils import read_n_from_end, Redis


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

