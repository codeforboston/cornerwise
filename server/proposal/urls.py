from django.conf.urls import url

from . import views
from . import feed

urlpatterns = [
    url(r"^list$", views.active_proposals),
    url(r"^view/(?P<pk>[0-9]+)", views.view_proposal,
        name="view-proposal"),
    # Feeds:
    url(r"^rss", feed.ReportsAndDecisionsFeed()),
    url(r"^atom", feed.ReportsAndDecisionsAtom()),
]
