from collections import defaultdict

from proposal.models import Change, Proposal
from proposal.views import proposal_json
from proposal.query import build_proposal_query


def find_updates(subscriptions, since):
    change_summary = defaultdict(dict)

    for subscription in subscriptions:
        query_dict = subscription.query_dict
        if not query_dict:
            return None

        query = build_proposal_query(query_dict)
        proposals = Proposal.objects.filter(query, updated__gt=since)

        if not proposals:
            continue

        ids = [proposal.pk for proposal in proposals]

        changes = Change.objects.filter(created_at__gt=since,
                                        proposal__in=ids)\
                                .order_by("created_at")
        for change in changes:
            if change.description:
                desc = change.description
            else:
                desc = ""

            change_summary[change.proposal_id][change.prop_path] = {
                "description": desc
            }

    summary = []
    for proposal in proposals:
        if proposal.pk in change_summary:
            summary.append({"proposal": proposal_json(proposal,
                                                      include_images=1,
                                                      include_documents=False),
                            "changes": change_summary[proposal.pk]})

    return summary
