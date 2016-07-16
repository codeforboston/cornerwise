from django.conf.urls import url
from task import views

urlpatterns = [
    url(r"^status$", views.task_status, name="task-status")
]
