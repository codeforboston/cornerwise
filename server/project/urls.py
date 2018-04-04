from django.urls import path

from . import views

urlpatterns = [
    path("list", views.list_projects, name="list-projects"),
    path("view/<int:pk>", views.view_project, name="view-project"),
]
