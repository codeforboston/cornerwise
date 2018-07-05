from datetime import datetime, timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from shared.logger import get_logger
from shared.mail import send as send_mail

from cornerwise.adapt import adapt
import site_config

from .models import Subscription
from . import mail

User = get_user_model()


@shared_task(bind=True)
@adapt
def send_user_updates(self, sub: Subscription, updates):
    """Sends an email to a user containing a summary of recent updates to a
    Subscription.

    """
    user = sub.user
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


@shared_task
@adapt
def send_deactivation_email(user: User):
    """Sends the email when a user is unsubscribed.
    """
    mail.send_deactivation_email(user)


@shared_task(bind=True)
@adapt
def resend_user_key(self, user: User):
    mail.send_login_link(user, get_logger(self))


@shared_task(bind=True)
@adapt
def send_subscription_confirmation_email(self, sub: Subscription):
    """
    """
    logger = get_logger(self)
    user = sub.user

    if not user.is_active:
        mail.send_welcome_email(sub)
        return

    if sub.active:
        return

    existing = None
    if sub.site_name:
        config = site_config.by_hostname(sub.site_name)
        if not config.allow_multiple_subscriptions:
            try:
                existing = user.subscriptions.active()\
                                             .filter(site_name=sub.site_name)\
                                             .exclude(pk=sub.id)[0]
            except IndexError:
                pass

    # Send an email to confirm the subscription change
    if existing:
        mail.send_replace_subscription_email(sub, existing, logger)
    else:
        mail.send_confirm_subscription_email(sub, logger)


@shared_task(bind=True)
def send_notifications(self, subscription_ids=None, since=None):
    """Check the Subscriptions and find those that have new updates since the last
    update was run.

    """
    logger = get_logger(self)
    if subscription_ids:
        subscriptions = Subscription.objects.filter(pk__in=subscription_ids)
    else:
        subscriptions = Subscription.objects.due(since)

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
@adapt
def send_staff_notification(self, sub: Subscription, title, message):
    mail.send_staff_notification_email(sub,
                                       title or "New Message", message,
                                       get_logger(self))


@shared_task(bind=True)
def cleanup_subscriptions(self):
    logger = get_logger(self)
    deleted_count, counts = Subscription.objects.stale().delete()
    subs_count = counts["user.Subscription"]
    if subs_count:
        logger.info("Deleted %s unconfirmed subscriptions", subs_count)


# Database hook:
@receiver(
    post_save,
    sender=Subscription,
    dispatch_uid="send_subscription_confirmation_email")
def subscription_created(**kwargs):
    if kwargs["created"]:
        subscription = kwargs["instance"]
        send_subscription_confirmation_email.delay(subscription.pk)
