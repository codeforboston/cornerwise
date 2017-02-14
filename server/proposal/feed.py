from django.core.urlresolvers import reverse
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from .models import Proposal


class ReportsAndDecisionsFeed(Feed):
    title = "Somerville Reports and Decisions"
    link = "/proposals/"
    description = ""

    def items(self, request):
        # TODO: Implement filters
        return Proposal.objects.order_by("-modified")\
                               .select_related()

    def item_title(self, item):
        return item.summary

    def item_description(self, item):
        return "{p.address} - {p.description}".format(p=item)

    def item_pubdate(self, item):
        return item.created

    def item_updateddate(self, item):
        return item.modified

    # Attached documents:

    # Note: RSS feeders are evidently not required to support multiple
    # enclosures. We should come up with a sensible heuristic for
    # choosing which document is most relevant for inclusion.  Probably
    # the first 'decision' document if present, else something like
    # 'plans'.
    def item_enclosure_url(self, item):
        document = item.document_set.all()[0]

        if document:
            return document.url

    # TODO: Detect the appropriate MIME type
    item_enclosure_mime_type = "application/pdf"

    item_copyright = ""


class ReportsAndDecisionsAtom(ReportsAndDecisionsFeed):
    feed_type = Atom1Feed
    subtitle = ReportsAndDecisionsFeed.description
