from datetime import datetime, timedelta
from urllib import request

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from shared.logger import get_logger
from shared.mail import send as send_mail

from .models import Subscription
from . import mail

User = get_user_model()


@shared_task(bind=True)
def send_user_updates(self, sub_id, updates):
    """Sends an email to a user containing a summary of recent updates to a
    Subscription.

    """
    sub = Subscription.objects.get(pk=user_id)
    send_mail(user.email, "Cornerwise: New Updates", "updates",
              mail.updates_context(sub, updates),
              logger=get_logger(self))


def send_subscription_updates(subscription, since):
    """If there are any recent changes relevant to the given Subscription,
    create a task to send email to the subscription owner.
    """
    if not since:
        since = subscription.last_notified
    updates = subscription.summarize_updates(since)
    if updates["total"]:
        send_user_updates.delay(subscription.pk, updates)
        return True


def send_user_welcome(subscription):
    """Send an email requesting confirmation of a subscription.
    """
    send_mail(subscription.user.email, "Cornerwise: Welcome", "welcome",
              mail.welcome_context(subscription))


@shared_task
def send_deactivation_email(user_id):
    """Sends the email when a user is unsubscribed.
    """
    user = User.objects.get(pk=user_id)
    send_mail(user.email, "Cornerwise: Unsubscribed", "account_deactivated",
              mail.deactivate_context(user), use_generic_template=True)


@shared_task(bind=True)
def send_subscription_confirmation_email(self, sub_id):
    """When a new Subscription is created, check if the User has existing
    Subscription(s). If s/he does and if LIMIT_SUBSCRIPTIONS is set to True,
    send an email asking the user to confirm the new subscription and replace
    the old one.
    """
    logger = get_logger(self)
    subscription = Subscription.objects.select_related("user").get(pk=sub_id)
    user = subscription.user

    if not user.is_active:
        send_user_welcome(subscription)
        return

    # Revisit this if we turn off subscription limiting. We'd still want the
    # user to confirm the new subscription, since we don't have logins.
    if not settings.LIMIT_SUBSCRIPTIONS or \
       subscription.active:
        return

    try:
        existing = user.subscriptions.filter(active=True)[0]
    except IndexError:
        # The user doesn't have any active Subscriptions
        return

    # Prefetch the minimap images. The CDN will cache it, and subsequent loads
    # will have much lower latency:
    request.urlopen(subscription.minimap_src).close()
    request.urlopen(existing.minimap_src).close()

    send_mail(user.email, "Cornerwise: Confirm New Subscription",
              "replace_subscription", mail.replace_subscription_context(subscription),
              logger=logger)


@shared_task(bind=True)
def send_notifications(self, subscription_ids=None, since=None):
    """Check the Subscriptions and find those that have new updates since the last
    update was run.

    """
    logger = get_logger(self)
    if subscription_ids:
        subscriptions = Subscription.objects.filter(pk__in=subscription_ids)
    else:
        before = datetime.utcnow() - timedelta(days=7)
        subscriptions = Subscription.objects.filter(active=True,
                                                    last_notified__lte=before)

    sent = []
    for subscription in subscriptions:
        if send_subscription_updates(subscription, since):
            sent.append(subscription.pk)

    if sent:
        logger.info("Sent updates for %s subscription(s)", len(sent))
        Subscription.objects.filter(pk__in=sent).mark_sent()
    else:
        logger.info("No updates sent")


@shared_task(bind=True)
def send_staff_notification(self, sub_id, title, message):
    sub = Subscription.objects.get(pk=sub_id)
    title = title or "New Message"
    send_mail(sub.user.email, f"Cornerwise: {title}", "staff_notification",
              mail.staff_notification_context(sub, title, message),
              logger=get_logger(self))


# Database hook:
@receiver(
    post_save,
    sender=Subscription,
    dispatch_uid="send_subscription_confirmation_email")
def subscription_created(**kwargs):
    if kwargs["created"]:
        subscription = kwargs["instance"]
        send_subscription_confirmation_email.delay(subscription.pk)
