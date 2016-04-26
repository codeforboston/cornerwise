from datetime import datetime, timedelta
import sendgrid

from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
from django.template.loader import render_to_string


from cornerwise import celery_app
from cornerwise.utils import make_absolute_url

from .models import Subscription, User
from .changes import find_updates
# from proposal.models import Proposal
# from proposal.query import build_proposal_query

logger = get_task_logger(__name__)


if getattr(settings, "SENDGRID_API_KEY", None):
    SG = sendgrid.SendGridClient(settings.SENDGRID_API_KEY,
                                 raise_errors=True)
else:
    SG = None


@celery_app.task()
def send_subscription_updates(user, updates):
    html = ""
    text = ""

    if SG:
        message = sendgrid.Mail(subject="Cornerwise: New Updates",
                                html=html,
                                text=text,
                                from_email=settings.EMAIL_ADDRESS)
        message.add_to("{first} {last} <{email}>".
                       format(first=user.first_name,
                              last=user.last_name,
                              email=user.email))

        status, msg = SG.send(message)
        logger.info("Sent subscription updates to %s (status %i)",
                    user.email, status)
        return status
    else:
        logger.info("SendGrid is not configured")
        logger.info("Generated email:", html)
        return -1


@celery_app.task(name="project.send_user_key")
def send_user_key(user):
    profile = user.profile
    if not profile.token:
        profile.generate_token()

    # Render HTML and text templates:
    path = reverse("user-login", kwargs={"token": profile.token,
                                         "pk": user.pk})
    context = {"user": user,
               "confirm_url": make_absolute_url(path)}
    html = render_to_string("email/confirm.djhtml", context)
    text = render_to_string("email/confirm.djtxt", context)

    if SG:
        message = sendgrid.Mail(
            subject="Hi!  Please confirm your Cornerwise settings",
            html=html,
            text=text,
            from_email=settings.EMAIL_ADDRESS)
        message.add_to(user.email)

        status, msg = SG.send(message)

        logger.info("Sent welcome email to %s (status %i)",
                    user.email, status)
    else:
        logger.info("SendGrid not available.  Generated email:", html)


@celery_app.task()
def run_notifications(subscriptions=None, since=None):
    """Check the Subscriptions and find those that have new updates since the last
    update was run.
    """
    if subscriptions is None:
        subscriptions = Subscription.objects.all()

    if since is None:
        since = datetime.now() - timedelta(days=7)

    for subscription in subscriptions:
        updates = find_updates(subscription, since)
        if updates:
            send_subscription_updates(subscription.user, updates)


# Database hooks:
def user_created(kls, **kwargs):
    user = kwargs["instance"]
    created = kwargs["created"]
    if not created:
        return

    send_user_key.delay(user)


def set_up_hooks():
    post_save.connect(user_created, User,
                      dispatch_uid="send_confirmation_email")
