"""Utilities for rendering emails.
"""
import logging

import toronado
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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
    email = email if isinstance(email, list) else [email]
    recipients = [{"email": addr} if isinstance(addr, str) else addr
                  for addr in email]

    mail = EmailMultiAlternatives(
        from_email=f"{settings.EMAIL_NAME} <{settings.EMAIL_ADDRESS}>",
        subject=subject,
        body="",
        to=recipients
    )
    mail.template_id = template_id
    mail.substitutions = substitutions

    if content:
        mail.attach_alternative(content, "text/html")

    mail.send()
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

    html = toronado.from_string(html).decode("utf-8")

    return (html, text)


def send_template(email, subject, template_name, context=None, logger=logger):
    """Construct and send an email with subject `subject` to `email`, using the
    named email template.
    """
    context = context or {}
    html, text = render_email_body(template_name, context)
    logger.info("Generated email: %s", html)

    mail = EmailMultiAlternatives(
        from_email=f"{settings.EMAIL_NAME} <{settings.EMAIL_ADDRESS}>",
        subject=subject,
        body=text,
        to=(email if isinstance(email, list) else [email]))
    mail.attach_alternative(html, "text/html")
    mail.send()
    logger.info("Sent '%s' email to %s", template_name,
                email)
