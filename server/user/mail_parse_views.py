from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import logging

import site_config
from shared import mail
from . import tasks

logger = logging.getLogger(__name__)

User = get_user_model()


def send_fowarded_message(users, from_email, text, to_username="admin"):
    emails = [user.email for user in users]
    mail.send(emails, "Cornerwise: Received Message",
              "forwarded", {"text": text,
                            "from": from_email,
                            "to_username": to_username})


def forward_mail(username, hostname, from_email, text):
    """Forwards messages sent to @cornerwise.org (or other) addresses. If the
    username is 'admin', the message is forwarded to all admin users with an
    email address configured. If the username matches a site configuration, all
    members of the corresponding django.auth.models.Group will get the message.
    """
    try:
        users = User.objects.exclude(email="")
        if username == "admin":
            users = users.filter(is_staff=True)
        else:
            config = site_config.by_name(username)
            if config and config.group_name:
                users = users.filter(groups__name=config.group_name)
            else:
                users = users.filter(groups__name=username)
                if not users:
                    users = [users.get(username=username, is_staff=True)]
        send_fowarded_message(users, from_email, text, username)
        return HttpResponse(f"OK: Forwarded email to {len(users)} user(s)", status=200)
    except User.DoesNotExist:
        logger.warn(f"Received email for unknown user '{username}' from {from_email}")
        return HttpResponse("OK: Not sent", status=200)


# When email is sent to @cornerwise.org, SendGrid parses it and posts the
# results to this view:
@csrf_exempt
def mail_inbound(request):
    """Handles email sent to addresses under the MX domain configured with
    SendGrid, e.g., admin@cornerwise.org. If the username is 'noreply' or
    'cornerwise', the body of the message is interpreted as actions. For
    example, a user can reply to an updates notification with 'unsubscribe' to
    turn off notifications. For all other usernames, attempt to forward email
    to the appropriate admins.

    See https://sendgrid.com/docs/API_Reference/Webhooks/parse.html for
    documentation of the POST fields.

    """
    try:
        # The SendGrid webhook URL may contain a 'key' parameter that must
        # match the key in settings. This provides some assurance that 
        parse_key = settings.SENDGRID_PARSE_KEY
        if parse_key and request.GET.get("key", "") != parse_key:
            logger.warning("Received mail_inbound request with a bad key")
            return HttpResponse("NOK: bad key", status=403)

        from_email = request.POST["from"]
        body = request.POST["text"]

        (username, hostname) = request.POST["to"].casefold().split("@", 1)
        if username not in {"cornerwise", "noreply"}:
            return forward_mail(username, hostname, from_email, body)

        user = User.objects.get(email=from_email)
        lines = request.POST["text"].split("\n")
        for line in lines:
            command = line.strip().split(" ")[0]
            if command in email_commands:
                email_commands(request, user)
                logger.info(f"Successfully processed email from {from_email}")
                return HttpResponse("OK", status=200)

        logger.warning(f"Email from {from_email} contained no recognized commands")

        return HttpResponse("NOK: no commands recognized", status=200)
    except KeyError as kerr:
        logger.exception(f"Missing required key in POST data")
    except User.DoesNotExist:
        logger.warning("Received an email from unknown user %s", request.POST["from"])

    # SendGrid will retry if there's a status code other than 200.
    return HttpResponse("NOK: invalid message", status=200)


def deactivate_account(request, user):
    user.profile.deactivate()
    tasks.send_deactivation_email.delay(user.id)


email_commands = {"deactivate": deactivate_account}
