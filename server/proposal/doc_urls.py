from django.urls import include, path

from . import views


urlpatterns = [
    path("<int:pk>/", include([
        path("", views.view_document, name="view-document"),
        path("download/", views.download_document, name="download-document"),
    ]))
]
