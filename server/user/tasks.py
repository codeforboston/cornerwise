from datetime import datetime, timedelta
from urllib import request

import sendgrid

from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from cornerwise import celery_app
from cornerwise.utils import make_absolute_url

from .models import Subscription, UserProfile
from .changes import summarize_subscription_updates
# from proposal.models import Proposal
# from proposal.query import build_proposal_query

logger = get_task_logger(__name__)

if getattr(settings, "SENDGRID_API_KEY", None):
    SG = sendgrid.SendGridAPIClient(
        apikey=settings.SENDGRID_API_KEY, raise_errors=True)
else:
    SG = None


def has_name(u):
    return u.first_name and u.last_name


def send_mail(user, subject, template_name, context={}, content=None):
    try:
        template_id = settings.SENDGRID_TEMPLATES[template_name]
    except:
        # Fall back to Django templates
        return send_mail_template(user, subject, template_name, context)

    substitutions = {"-{}-".format(k): str(v) for k, v in context.items()}
    substitutions["-user-"] = user.profile.addressal
    substitutions["-unsubscribe_link-"] = user.profile.unsubscribe_url

    data = {
        "personalizations": [{
            "to": [{
                "email": user.email
            }],
            "substitutions": substitutions,
            "subject": subject,
        }],
        "from": {
            "email": settings.EMAIL_ADDRESS,
            "name": settings.EMAIL_NAME
        },
        "template_id": template_id
    }

    if content:
        data["content"] = [{"type": "text/html", "value": content}]

    try:
        SG.client.mail.send.post(request_body=data)
    except request.HTTPError as err:
        return (False, err)
    else:
        logger.info("Email sent to {}".format(user.email))
        return True


def send_mail_template(user, subject, template_name, context={}):
    context = context.copy()
    context["user"] = user.profile.addressal()
    html = render_to_string("email/" + template_name + ".djhtml", context)
    try:
        text = render_to_string("email/" + template_name + ".djtxt", context)
    except TemplateDoesNotExist:
        text = strip_tags(html)

    if SG:
        message = sendgrid.Mail(
            subject=subject,
            html=html,
            text=text,
            from_email=settings.EMAIL_ADDRESS)
        if has_name(user):
            message.add_to("{first} {last} <{email}>".format(
                first=user.first_name, last=user.last_name, email=user.email))
        else:
            message.add_to(user.email)
        status, msg = SG.send(message)
        logger.info("Sent '%s' email to %s (status %i)", template_name,
                    user.email, status)
    else:
        logger.info("SendGrid not available. Generated email: %s", html)


@celery_app.task()
def send_subscription_updates(user_id, updates):
    user = User.objects.get(pk=user_id)
    send_mail(user, "Cornerwise: New Updates", "updates", {})


@celery_app.task(name="user.send_user_key")
def send_user_key(user_id):
    profile = UserProfile.objects.get(user_id=user_id)
    if not profile.token:
        profile.generate_token()

    # TODO: We want to send the user a summary of the first subscription created

    # Render HTML and text templates:
    context = {"confirm_url": make_absolute_url(profile.manage_url)}
    # send_mail(profile.user, "Cornerwise: Please confirm your email",
    #           "confirm", context)
    send_mail(profile.user, "Cornerwise: Welcome", "welcome", context)


@celery_app.task(name="user.resend_user_key")
def resend_user_key(user_id):
    profile = UserProfile.objects.get(user_id=user_id)
    if not profile.token:
        profile.generate_token()

    send_mail(profile.user, "Cornerwise: Your Account", "login_link",
              {"user": profile.user})


@celery_app.task()
def send_deactivation_email(user_id):
    user = User.objects.get(pk=user_id)
    send_mail(user, "Cornerwise: Account Disabled", "account_deactivated")


@celery_app.task()
def send_reset_email(user_id):
    user = User.objects.get(pk=user_id)
    send_mail(user, "Cornerwise: Login Reset", "account_reset")


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

    # The current user flow should make it impossible for a confirmed user to
    existing = user.subscriptions.filter(active=True).count()
    if existing <= 1:
        return

    context = {
        "subscription": subscription.readable_description,
        "minimap_src": subscription.minimap_src,
        "confirmation_link": make_absolute_url(subscription.confirmation_url)
    }
    send_mail(user, "Cornerwise: Confirm New Subscription",
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
        updates = summarize_subscription_updates(subscription, since)
        if updates:
            send_subscription_updates(subscription.user, updates)


# Database hooks:
def user_profile_created(**kwargs):
    if kwargs["created"]:
        profile = kwargs["instance"]
        send_user_key.delay(profile.user_id)


def subscription_created(**kwargs):
    if kwargs["created"]:
        subscription = kwargs["instance"]
        send_subscription_confirmation_email.delay(subscription.id)


def set_up_hooks():
    post_save.connect(
        user_profile_created,
        UserProfile,
        dispatch_uid="send_confirmation_email")
    post_save.connect(
        subscription_created,
        Subscription,
        dispatch_uid="send_subscription_confirmation_email")
