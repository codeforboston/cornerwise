from datetime import datetime, timedelta
from urllib import request
import pytz

from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from cornerwise import celery_app
from cornerwise.utils import make_absolute_url

from .models import Subscription, UserProfile
from . import changes, mail

logger = get_task_logger(__name__)


@celery_app.task(name="user.send_user_updates")
def send_user_updates(user_id, updates):
    user = User.objects.get(pk=user_id)
    updates_html = render_to_string("changes.djhtml",
                                    {"changes": updates["changes"]})

    datefmt = lambda dt: datetime.fromtimestamp(dt).strftime("%A, %B %-d") if dt else ""
    fmt = "from {start} to {end}" if updates["end"] else "since {start}"
    date_range = fmt.format(
        start=datefmt(updates["start"]), end=datefmt(updates["end"]))

    mail.send(user, "Cornerwise: New Updates", "updates", {
        "updates": updates_html,
        "update_summary": changes.summary_line(updates),
        "date_range": date_range
    })


def send_subscription_updates(subscription, since):
    updates = changes.summarize_subscription_updates(subscription, since)
    if updates["total"]:
        send_user_updates.delay(subscription.user_id, updates)


def send_user_welcome(user, subscription):
    profile = user.profile
    if not profile.token:
        profile.generate_token()

    # Render HTML and text templates:
    context = {
        "confirm_url": make_absolute_url(profile.confirm_url),
        "minimap_src": subscription.minimap_src,
        "subscription-preview": subscription.minimap_src
    }
    mail.send(profile.user, "Cornerwise: Welcome", "welcome", context)


@celery_app.task()
def send_deactivation_email(user_id):
    user = User.objects.get(pk=user_id)
    mail.send(user, "Cornerwise: Unsubscribed", "account_deactivated")


@celery_app.task()
def send_subscription_confirmation_email(sub_id):
    """"
    When a new Subscription is created, check if the User has existing
    Subscription(s). If s/he does and if LIMIT_SUBSCRIPTIONS is set to True,
    send an email asking the user to confirm the new subscription and replace
    the old one.
    """
    subscription = Subscription.objects.select_related("user").get(pk=sub_id)
    user = subscription.user

    if not user.is_active:
        send_user_welcome(user, subscription)
        return

    # Revisit this if we turn off subscription limiting. We'd still want the
    # user to confirm the new subscription, since we don't have logins.
    if not settings.LIMIT_SUBSCRIPTIONS or \
       subscription.active:
        return

    try:
        existing = user.subscriptions.filter(active=True)[0]
    except:
        # The user doesn't have any active Subscriptions
        return

    # Prefetch the minimap images. The CDN will cache it, and subsequent loads
    # will have much lower latency:
    request.urlopen(subscription.minimap_src).close()
    request.urlopen(existing.minimap_src).close()

    context = {
        "subscription": subscription.readable_description,
        "minimap_src": subscription.minimap_src,
        "subscription-preview": subscription.minimap_src,
        "old_minimap_src": existing.minimap_src,
        "confirmation_link": make_absolute_url(subscription.confirm_url)
    }
    mail.send(user, "Cornerwise: Confirm New Subscription",
              "replace_subscription", context)


@celery_app.task(name="user.send_notifications")
def send_notifications(subscription_ids=None, since=None):
    """
    Check the Subscriptions and find those that have new updates since the last
    update was run.
    """
    if subscription_ids is None:
        subscriptions = Subscription.objects.filter(active=True)
    else:
        subscriptions = Subscription.objects.filter(pk__in=subscription_ids)

    if since is None:
        since = pytz.utc.localize(datetime.utcnow() - timedelta(days=7))

    for subscription in subscriptions:
        send_subscription_updates(subscription, since)


# Database hook:
@receiver(
    post_save,
    sender=Subscription,
    dispatch_uid="send_subscription_confirmation_email")
def subscription_created(**kwargs):
    if kwargs["created"]:
        subscription = kwargs["instance"]
        send_subscription_confirmation_email.delay(subscription.pk)
