from collections import defaultdict

from proposal.models import Changeset, Proposal
from proposal.views import proposal_json
from proposal.query import build_proposal_query

def summarize_subscription_updates(subscription, since, until):
    query_dict = subscription.query_dict
    if not query_dict:
        return None

    query = build_proposal_query(query_dict)

    # Find proposals that are new since the given date:
    proposals = Proposal.objects.filter(query, created__gt=since)

    new_ids = [proposal.pk for proposal in proposals]

    proposals_changed = Proposal.objects\
                                .exclude(pk__in=new_ids)\
                                .filter(query,
                                        updated__gt=since)
    if until:
        proposals_changed = proposals_changed.filter(updated__lte=until)

    if not proposals and not proposals_changed:
        return None

    # Only include changesets for proposals we're interested in:
    ids = [proposal.pk for proposal in proposals_changed]
    changes = Changeset.objects.filter(created_at__gt=since,
                                       proposal__in=ids)\
                                .order_by("created_at")

    summary = list({"proposal": proposal_json(p)} for p in proposals)
    prop_changes = defaultdict(list)
    attr_changes = defaultdict(list)
    for change in changes:
        change_dict = change.changes
        pchange_list = prop_changes[change.proposal_id]
        achange_list = attr_changes[change.proposal_id]
        pchange_list.extend(change_dict["properties"])
        achange_list.extend(change_dict["attributes"])
        summary.append({
            "proposal": proposal_json(change.proposal),
            "properties": pchange_list,
            "attributes": achange_list
        })



def find_updates(subscriptions, since, until=None):
    """
    Find and summarize changes that are relevant to the given subscriptions.

    :subscriptions: A collection of Subscription objects
    :since: datetime
    :until: datetime
    """
    for subscription in subscriptions:
        summary = summarize_subscription_updates(subscription,
                                                 since,
                                                 until)

        if summary:
            pass


    for proposal in proposals:
        if proposal.pk in change_summary:
            summary.append({"proposal": proposal_json(proposal,
                                                      include_images=1,
                                                      include_documents=False),
                            "changes": change_summary[proposal.pk]})

    return summary
