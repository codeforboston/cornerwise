from datetime import datetime, timedelta
import sendgrid

from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
from django.template.loader import render_to_string


from cornerwise import celery_app
from cornerwise.utils import make_absolute_url

from .models import Subscription
from .changes import find_updates
# from proposal.models import Proposal
# from proposal.query import build_proposal_query

logger = get_task_logger(__name__)


if getattr(settings, "SENDGRID_API_KEY", None):
    SG = sendgrid.SendGridClient(settings.SENDGRID_API_KEY,
                                 raise_errors=True)
else:
    SG = None


def has_name(u):
    return u.first_name and u.last_name


def send_mail(user, subject, template_name, context={}):
    context = context.copy()
    context["user"] = user
    context["profile"] = user.profile
    html = render_to_string("email/" + template_name + ".djhtml", context)
    text = render_to_string("email/" + template_name + ".djtxt", context)

    if SG:
        message = sendgrid.Mail(
            subject=subject,
            html=html,
            text=text,
            from_email=settings.EMAIL_ADDRESS)
        if has_name(user):
            message.add("{first} {last} <{email}>".
                        format(first=user.first_name,
                               last=user.last_name,
                               email=user.email))
        else:
            message.add(user.email)
        status, msg = SG.send(message)
        logger.info("Sent '%s' email to %s (status %i)",
                    template_name, user.email, status)
    else:
        logger.info("SendGrid not available. Generated email: %s", html)


@celery_app.task()
def send_subscription_updates(user, updates):
    send_mail(user, "Cornerwise: New Updates",
              "updates", {})


@celery_app.task(name="project.send_user_key")
def send_user_key(user):
    profile = user.profile
    if not profile.token:
        profile.generate_token()

    # Render HTML and text templates:
    path = reverse("user-login", kwargs={"token": profile.token,
                                         "pk": user.pk})
    context = {"confirm_url": make_absolute_url(path)}
    send_mail(user, "Cornerwise: Please confirm your email",
              "confirm", context)


@celery_app.task()
def send_deactivation_email(user):
    send_mail(user, "Cornerwise: Account Disabled", "account_deactivated")


@celery_app.task()
def send_reset_email(user):
    send_mail(user, "Cornerwise: Login Reset", "account_reset")


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
def user_created(**kwargs):
    if kwargs["created"]:
        send_user_key.delay(kwargs["instance"])


def set_up_hooks():
    post_save.connect(user_created, settings.AUTH_USER_MODEL,
                      dispatch_uid="send_confirmation_email")
