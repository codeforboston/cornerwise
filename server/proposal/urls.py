from django.conf.urls import include, url

from . import views
from . import feed

doc_urlpatterns = [
    url(r"^$", views.view_document, name="view-document"),
]

urlpatterns = [
    url(r"^list$", views.active_proposals),
    url(r"^closed$", views.closed_proposals),
    url(r"^view/(?P<pk>[0-9]+)", views.view_proposal, name="view-proposal"),

    # Feeds:
    url(r"^rss", feed.ReportsAndDecisionsFeed()),
    url(r"^atom", feed.ReportsAndDecisionsAtom()),
]
