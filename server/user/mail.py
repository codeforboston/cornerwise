import sendgrid

from celery.utils.log import get_task_logger
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import strip_tags


if getattr(settings, "SENDGRID_API_KEY", None):
    SG = sendgrid.SendGridAPIClient(
        apikey=settings.SENDGRID_API_KEY, raise_errors=True)
else:
    SG = None

logger = get_task_logger(__name__)


def has_name(u):
    return u.first_name and u.last_name


def send(user, subject, template_name, context={}, content=None):
    """
    Send an email to a user. If there is a SendGrid template id configured for
    the given template name, create substitutions from `context` so that `-key`
    in the template is replaced by the value of `key` in `context`.

    If there is no such SendGrid template, falls back to using a Django
    template in <templates>/email.
    """
    try:
        template_id = settings.SENDGRID_TEMPLATES[template_name]
    except:
        # Fall back to Django templates
        return send_template(user, subject, template_name, context)

    substitutions = {"-{}-".format(k): str(v) for k, v in context.items()}
    substitutions["-user-"] = user.profile.addressal
    substitutions["-unsubscribe_url-"] = user.profile.unsubscribe_url

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


def send_template(user, subject, template_name, context={}):
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

