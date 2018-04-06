"""Utilities for rendering emails.
"""
import logging

import requests
import sendgrid
import toronado
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from sendgrid.helpers import mail

if getattr(settings, "SENDGRID_API_KEY", None):
    SG = sendgrid.SendGridAPIClient(
        apikey=settings.SENDGRID_API_KEY, raise_errors=True)
else:
    SG = None

logger = logging.getLogger(__name__)


def send(email, subject, template_name=None, context=None, content=None,
         template_id=None, logger=logger):
    """
    Send an email to an email address. If there is a SendGrid template id
    configured for the given template name, create substitutions from `context`
    so that `-key-` in the template is replaced by the value of `key` in
    `context`.

    If there is no such SendGrid template, falls back to using a Django
    template in <templates>/email.

    """
    assert template_name or template_id, "missing argument"
    context = {} if context is None else context

    if not template_id:
        try:
            template_id = settings.SENDGRID_TEMPLATES[template_name]
        except KeyError:
            # Fall back to Django templates
            return send_template(email, subject, template_name, context)

    substitutions = {"-{}-".format(k): str(v) for k, v in context.items()}

    if not isinstance(email, list):
        email = [email]

    recipients = [{"email": addr} if isinstance(addr, str) else addr
                  for addr in email]

    data = {
        "personalizations": [{
            "to": recipients,
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


def render_email_body(template_name, context=None):
    """Generate text and HTML for an email body using the named email template,
    with substitutions provided by `context`.
    """
    context = {} if context is None else context
    html = render_to_string("email/" + template_name + ".djhtml", context)
    try:
        text = render_to_string("email/" + template_name + ".djtxt", context)
    except TemplateDoesNotExist:
        text = strip_tags(html)

    html = toronado.from_string(html)

    return (html, text)


def send_template(email, subject, template_name, context=None, logger=logger):
    """Construct and send an email with subject `subject` to `email`, using the
    named email template.
    """
    context = context or {}
    html, _text = render_email_body(template_name, context)
    logger.info("Generated email: %s", html)
    addressal = context.get("user")

    if SG:
        message = mail.Mail(
            mail.Email(settings.EMAIL_ADDRESS), subject,
            mail.Email(email, addressal or email),
            mail.Content("text/html", html))
        response = SG.client.mail.send.post(request_body=message.get())
        logger.info("Sent '%s' email to %s (response %s)", template_name,
                    email, response)
    else:
        logger.info("SendGrid not available. Generated email: %s", html)


def _get_sendgrid(url, params=None):
    response = requests.get(
        url, params,
        headers={"Authorization": f"Bearer {settings.SENDGRID_API_KEY}"})
    return response
