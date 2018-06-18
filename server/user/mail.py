from datetime import datetime

from django.template.loader import render_to_string

from django.contrib.auth import get_user_model

from utils import make_absolute_url

from shared.mail import send as send_mail
from . import changes, models

User = get_user_model()


def _make_user_context(subscription, context=None, user=None):
    context = {} if context is None else context
    site_name = (subscription and subscription.site_name) or (user and user.profile.site_name)
    context["hostname"] = site_name
    context["user"] = user or subscription.user
    context["subscription"] = subscription
    context["site_root"] = make_absolute_url("/", site_name)
    return context


def deactivate_context(user):
    return {"user": user,
            "subscriptions": user.subscriptions.filter(active=True)}


def updates_context(sub, updates):
    """Constructs the context for the subscription updates email.
    """
    updates_html = render_to_string("changes.djhtml",
                                    {"changes": updates["changes"],
                                     "hostname": sub.site_name})

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
    return _make_user_context(subscription, {
        "salutation": "Welcome to Cornerwise! Please confirm your subscription"
    })


def confirm_context(subscription):
    """Works like welcome, but the user is already registered.
    """
    return _make_user_context(subscription, {
        "salutation": "Please confirm your new subscription"
    })


def replace_subscription_context(subscription, existing):
    return _make_user_context(subscription, {
        "existing": existing,
    })


def staff_notification_context(subscription, title, message):
    """
    Context passed to templates for messages sent by staff.
    """
    return _make_user_context(subscription, {
        "message": message,
        "title": title
    })


def send_welcome_email(subscription, logger=None):
    send_mail(subscription.user.email, "Cornerwise: Please Confirm", "welcome",
              welcome_context(subscription), logger=logger)


def send_replace_subscription_email(subscription, existing, logger=None):
    send_mail(
        subscription.user.email, "Cornerwise: Confirm Subscription Change",
        "replace_subscription",
        replace_subscription_context(subscription, existing),
        logger=logger)


def send_confirm_subscription_email(subscription, logger=None):
    send_mail(subscription.user.email, "Cornerwise: Confirm Subscription",
              "welcome", confirm_context(subscription), logger=logger)


def send_staff_notification_email(subscription, title, message, logger=None):
    send_mail(subscription.user.email, f"Cornerwise: {title}", "staff_notification",
              staff_notification_context(subscription, title, message),
              logger=logger)


def send_updates_email(subscription, since, updates, logger=None):
    send_mail(subscription.user.email, "Cornerwise: New Updates", "updates",
              updates_context(subscription, updates),
              logger=logger)


def send_login_link(user, logger=None):
    send_mail(user.email, "Cornerwise: Manage Your Account", "login_link",
              _make_user_context(None, user=user))
