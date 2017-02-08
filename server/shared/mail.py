import logging
from urllib import request

import sendgrid
from sendgrid.helpers import mail


from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import strip_tags


if getattr(settings, "SENDGRID_API_KEY", None):
    SG = sendgrid.SendGridAPIClient(
        apikey=settings.SENDGRID_API_KEY, raise_errors=True)
else:
    SG = None

logger = logging.getLogger(__name__)


def send(email, subject, template_name, context={}, content=None):
    """
    Send an email to an email address. If there is a SendGrid template id
    configured for the given template name, create substitutions from `context`
    so that `-key-` in the template is replaced by the value of `key` in
    `context`.

    If there is no such SendGrid template, falls back to using a Django
    template in <templates>/email.

    """
    try:
        template_id = settings.SENDGRID_TEMPLATES[template_name]
    except:
        # Fall back to Django templates
        return send_template(email, subject, template_name, context)

    substitutions = {"-{}-".format(k): str(v) for k, v in context.items()}

    data = {
        "personalizations": [{
            "to": [{
                "email": email
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

    SG.client.mail.send.post(request_body=data)
    logger.info("Email sent to {}".format(email))
    return True


def send_template(email, subject, template_name, context={}):
    context = context.copy()
    html = render_to_string("email/" + template_name + ".djhtml", context)
    addressal = context.get("user")
    try:
        text = render_to_string("email/" + template_name + ".djtxt", context)
    except TemplateDoesNotExist:
        text = strip_tags(html)

    if SG:
        message = mail.Mail(mail.Email(settings.EMAIL_ADDRESS),
                            subject,
                            mail.Email(email, addressal),
                            mail.Content("text/html", html))
        response = SG.client.mail.send.post(request_body=message.get())
        logger.info("Sent '%s' email to %s (response %s)", template_name,
                    email, response)
    else:
        logger.info("SendGrid not available. Generated email: %s", html)
