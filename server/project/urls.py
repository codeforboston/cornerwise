from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r"^list/$", views.list_projects, name="list-projects"),
    url(r"^view/(?P<pk>[0-9]+)$", views.view_project, name="view-project"),
]
