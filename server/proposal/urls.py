from django.conf import settings
from django.conf.urls import url

from . import views
from . import feed

doc_urlpatterns = [
    url(r"^$", views.view_document, name="view-document"),
]

urlpatterns = [
    url(r"^list$", views.list_proposals, name="list-proposals"),
    url(r"^closed$", views.closed_proposals),
    url(r"^view$", views.view_proposal),
    url(r"^view/(?P<pk>[0-9]+)$", views.view_proposal, name="view-proposal"),
    url(r"^events$", views.list_events, name="list-events"),
    url(r"^event/(?P<pk>[0-9]+)$", views.view_event),
    url(r"^image/(?P<pk>[0-9]+)$", views.view_image),
    url(r"^image$", views.view_image),

    # Feeds:
    url(r"^rss", feed.ReportsAndDecisionsFeed()),
    url(r"^atom", feed.ReportsAndDecisionsAtom()),
]

if settings.DEBUG:
    urlpatterns += [
        url(r"^images$", views.list_images),
    ]
