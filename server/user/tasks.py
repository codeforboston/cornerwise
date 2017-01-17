from datetime import datetime, timedelta
from urllib import request

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


@celery_app.task(name="user.send_updates")
def send_subscription_updates(user_id, updates):
    user = User.objects.get(pk=user_id)
    updates_html = render_to_string("email/changes.djhtml",
                                    {"changes": updates})
    mail.send_template(user, "Cornerwise: New Updates", "updates",
                       {"updates": updates_html})


@celery_app.task(name="user.send_user_key")
def send_user_key(user_id, created):
    if not created:
        return

    profile = UserProfile.objects.get(user_id=user_id)
    if not profile.token:
        profile.generate_token()

    # TODO: We want to send the user a summary of the first subscription created

    # Render HTML and text templates:
    context = {"confirm_url": make_absolute_url(profile.confirm_url)}
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

    if not user.is_active or \
       not settings.LIMIT_SUBSCRIPTIONS or \
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
        since = datetime.now() - timedelta(days=7)

    for subscription in subscriptions:
        updates = changes.summarize_subscription_updates(subscription, since)
        if updates:
            send_subscription_updates(subscription.user, updates)


# Database hooks:
@receiver(post_save, sender=UserProfile, dispatch_uid="send_confirmation_email")
def user_profile_created(**kwargs):
    profile = kwargs["instance"]
    send_user_key.delay(kwargs["instance"].user_id, kwargs["created"])


@receiver(post_save, sender=Subscription, dispatch_uid="send_subscription_confirmation_email")
def subscription_created(**kwargs):
    if kwargs["created"]:
        subscription = kwargs["instance"]
        send_subscription_confirmation_email.delay(subscription.pk)
