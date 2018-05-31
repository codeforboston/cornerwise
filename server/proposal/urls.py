from django.conf import settings
from django.urls import path

from . import feed, views

doc_urlpatterns = [
    path("", views.view_document, name="view-document"),
]

urlpatterns = [
    path("list", views.list_proposals, name="list-proposals"),
    path("view", views.view_proposal),
    path("view/<int:pk>", views.view_proposal, name="view-proposal"),
    path("events", views.list_events, name="list-events"),
    path("event/<int:pk>", views.view_event, name="event"),
    path("layers", views.list_layers),
    path("image/<int:pk>", views.view_image),
    path("image", views.view_image),

    # Feeds:
    path("rss", feed.ReportsAndDecisionsFeed()),
    path("atom", feed.ReportsAndDecisionsAtom()),
]

if settings.DEBUG:
    urlpatterns += [
        path("images", views.list_images),
    ]
