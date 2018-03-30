from datetime import datetime

from cornerwise.utils import make_absolute_url
from django.template.loader import render_to_string

from . import changes, models


def _make_user_context(user, context):
    context = context.copy() if context else {}

    try:
        context["user"] = user.profile.addressal
        context["unsubscribe_url"] = make_absolute_url(user.profile.unsubscribe_url)
    except models.UserProfile.DoesNotExist:
        context["user"] = "Unknown"
        context["unsubscribe_url"] = make_absolute_url("/")
    return context


def updates_context(user, updates):
    """Constructs the context for the subscription updates email.
    """
    updates_html = render_to_string("changes.djhtml",
                                    {"changes": updates["changes"]})

    datefmt = lambda dt: datetime.fromtimestamp(dt).strftime("%A, %B %-d") if dt else ""
    fmt = "from {start} to {end}" if updates["end"] else "since {start}"
    date_range = fmt.format(
        start=datefmt(updates["start"]), end=datefmt(updates["end"]))

    return _make_user_context(user, {
        "updates": updates_html,
        "update_summary": changes.summary_line(updates),
        "date_range": date_range
    })


def welcome_context(subscription):
    """Constructs the context for rendering the welcome email.
    """
    user = subscription.user
    profile = user.profile
    if not profile.token:
        profile.generate_token()

    return {
        "confirm_url": make_absolute_url(profile.confirm_url),
        "minimap_src": subscription.minimap_src,
        "subscription-preview": subscription.minimap_src
    }


def confirmation_context(subscription):
    try:
        user = subscription.user
        existing = user.subscriptions.filter(active=True).exists()
    except IndexError:
        # The user doesn't have any active Subscriptions
        return
    return {
        "subscription": subscription.readable_description,
        "minimap_src": subscription.minimap_src,
        "subscription-preview": subscription.minimap_src,
        "old_minimap_src": existing.minimap_src,
        "confirmation_link": make_absolute_url(subscription.confirm_url)
    }
