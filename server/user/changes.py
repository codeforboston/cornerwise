from collections import defaultdict, OrderedDict

from proposal.models import Changeset, Document, Image, Proposal
from proposal.views import proposal_json
from proposal.query import build_proposal_query


def summarize_query_updates(query, since, until=None):
    # Find proposals that are NEW since the given date:
    proposals = Proposal.objects.filter(created__gt=since, **query,)
    new_ids = {proposal.pk for proposal in proposals}

    # Find proposals that have *changed*, but which are not new:
    proposals_changed = Proposal.objects\
                                .exclude(pk__in=new_ids)\
                                .filter(updated__gt=since, **query)
    if until:
        proposals_changed = proposals_changed.filter(updated__lte=until)

        # Start with the new proposals:
    summary = OrderedDict((p.id, {
        "proposal": proposal_json(
            p, include_images=1, include_documents=False),
        "new": True
    }) for p in proposals)

    if proposals_changed:
        # Only include changesets for proposals we're interested in:
        ids = [proposal.pk for proposal in proposals_changed]
        changes = Changeset.objects.filter(created__gt=since,
                                           proposal__in=ids)\
                                   .order_by("created")

        prop_changes = defaultdict(list)
        attr_changes = defaultdict(list)
        for change in changes:
            change_dict = change.changes
            pchange_list = prop_changes[change.proposal_id]
            achange_list = attr_changes[change.proposal_id]
            pchange_list.extend(change_dict["properties"])
            achange_list.extend(change_dict["attributes"])

        for p in proposals_changed:
            summary[p.id] = {
                "proposal": proposal_json(
                    p, include_images=1, include_documents=False),
                "new": False,
                "properties": prop_changes[p.id],
                "attributes": attr_changes[p.id],
                "documents": [],
                "images": []
            }

    # Find new Documents:
    documents = Document.objects.filter(
        proposal__in=proposals_changed, created__gt=since)
    if until:
        documents = documents.filter(updated__lte=until)

    for doc in documents:
        if doc.proposal_id in summary:
            summary[doc.proposal_id]["documents"].append(doc.to_dict())

    # Find new Images:
    images = Image.objects.filter(
        proposal__in=proposals_changed, created__gt=since)
    if until:
        images = images.filter(updated__lte=until)

    for image in images:
        if image.proposal_id in summary:
            summary[image.proposal_id]["images"].append(image.to_dict())

    return summary


def summarize_subscription_updates(subscription, since, until=None):
    """Generates a dictionary describing the updates relevant to the given
    Subscription that occurred after `since` through `until` (if given).

    :subscription: a subscription with a `query_dict` property containing a
    dictionary suitabe for building a proposal query.
    :since: a datetime
    :until: datetime

    :returns: a dictionary with proposal ids as keys and dictionaries as
    values. The dictionaries
    """
    query_dict = subscription.query_dict
    if query_dict is None:
        return None

    query = build_proposal_query(query_dict)
    # Don't include changes that predate the Subscription:
    since = max(subscription.created, since)
    return summarize_query_updates(query, since, until)


def find_updates(subscription, since, until=None):
    """Find and summarize changes that are relevant to the given subscriptions.

    Note that this is not very scalable, but frankly, I don't think it needs to
    be. There are operations-level strategies for scaling that wouldn't require
    too much to be changed here.

    :subscription: A collection of Subscription objects
    :since: datetime
    :until: datetime

    """
    for subscription in subscriptions:
        summary = summarize_subscription_updates(subscription, since, until)

    return summary
