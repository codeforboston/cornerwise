from django.urls import path

from task import views


urlpatterns = [
    path("status", views.task_status, name="task-status"),
    path("statuses", views.task_statuses, name="task-statuses"),
]
