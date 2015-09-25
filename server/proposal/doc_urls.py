from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r"^(?P<pk>[0-9]+)/", include([
        url(r"^$", views.view_document, name="view-document"),
        url(r"^download/$", views.download_document, name="download-document"),
    ]))
]
