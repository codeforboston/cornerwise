from datetime import datetime

from django.template.loader import render_to_string

from django.contrib.auth import get_user_model

from utils import make_absolute_url

from . import changes, models

User = get_user_model()


def _make_user_context(subscription, context):
    user = subscription.user
    # context = context.copy() if context else {}

    try:
        context["user"] = user.profile.addressal or user.email
        context["unsubscribe_url"] = make_absolute_url(user.profile.unsubscribe_url,
                                                       subscription.site_name)
    except models.UserProfile.DoesNotExist:
        context["user"] = "Unknown"
        context["unsubscribe_url"] = make_absolute_url("/", subscription.site_name)
    context["site_root"] = make_absolute_url("/", subscription.site_name)
    return context


def updates_context(sub, updates):
    """Constructs the context for the subscription updates email.
    """
    updates_html = render_to_string("changes.djhtml",
                                    {"changes": updates["changes"]})

    datefmt = lambda dt: datetime.fromtimestamp(dt).strftime("%A, %B %-d") if dt else ""
    fmt = "from {start} to {end}" if updates["end"] else "since {start}"
    date_range = fmt.format(
        start=datefmt(updates["start"]), end=datefmt(updates["end"]))

    return _make_user_context(sub, {
        "updates": updates_html,
        "update_summary": changes.summary_line(updates),
        "date_range": date_range
    })


def welcome_context(subscription):
    """Constructs the context for rendering the welcome email.
    """
    profile = subscription.user.profile
    if not profile.token:
        profile.generate_token()

    return _make_user_context(subscription, {
        "confirm_url": make_absolute_url(profile.confirm_url, subscription.site_name),
        "minimap_src": subscription.minimap_src,
        "subscription-preview": subscription.minimap_src
    })


def replace_subscription_context(subscription, existing):
    return {
        "subscription": subscription.readable_description,
        "minimap_src": subscription.minimap_src,
        "old_minimap_src": existing.minimap_src,
        "confirmation_link": make_absolute_url(subscription.confirm_url, subscription.site_name)
    }


def staff_notification_context(subscription, title, message):
    """
    Context passed to templates for messages sent by staff.
    """
    return _make_user_context(subscription, {
        "message": message,
        "title": title
    })
