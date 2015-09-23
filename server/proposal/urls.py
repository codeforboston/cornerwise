from django.conf.urls import url

from . import views
from . import feed

urlpatterns = [
    url(r"^list$", views.active_proposals),
    url(r"^closed$", views.closed_proposals),
    url(r"^view/(?P<pk>[0-9]+)", views.view_proposal, name="view-proposal"),
    url(r"^doc/(?P<pk>[0-9]+)", views.view_document, name="view-document"),
    # Feeds:
    url(r"^rss", feed.ReportsAndDecisionsFeed()),
    url(r"^atom", feed.ReportsAndDecisionsAtom()),
]
