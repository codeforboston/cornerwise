from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from .models import Proposal

class ReportsAndDecisionsFeed(Feed):
    title = "Somerville Reports and Decisions"
    link = "/proposals/"
    description = ""

    def items(self):
        return Proposal.objects.order_by("-modified")

    def item_title(self, item):
        return item.summary

    def item_description(self, item):
        return "{p.address} - {p.description}".format(p=item)

    def item_pubdate(self, item):
        return item.created

    def item_updateddate(self, item):
        return item.modified

    item_copyright = ""

class ReportsAndDecisionsAtom(ReportsAndDecisionsFeed):
    feed_type = Atom1Feed
    subtitle = ReportsAndDecisionsFeed.description
