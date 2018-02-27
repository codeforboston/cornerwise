from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from utils import read_n_from_end


is_superuser = user_passes_test(lambda user: user.is_superuser, "/admin")


@is_superuser
def celery_logs(request):
    nlines = int(request.GET.get("n", "100"))
    with open("logs/celery_tasks.log", "rb") as log:
        log_lines = read_n_from_end(log, nlines)

    return render(request, "admin/log_view.djhtml",
                  {"log_name": "Celery Tasks Log",
                   "lines": log_lines})
