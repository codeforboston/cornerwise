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

generic_id = settings.SENDGRID_TEMPLATES.get("generic")


def send(recipients, subject, template_name=None, context=None, content=None,
         template_id=None, logger=logger, 
         sendgrid_templates=settings.SENDGRID_TEMPLATES, generic_id=generic_id):
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
            # TODO Use site config for template lookup
            template_id = sendgrid_templates[template_name]
        except KeyError:
            if generic_id:
                try:
                    context = render_generic_body(template_name, context)
                    template_id = generic_id
                except TemplateDoesNotExist:
                    pass

    if not template_id:
        # Fall back to Django templates
        return send_template(recipients, subject, template_name, context)

    substitutions = {"-{}-".format(k): str(v) for k, v in context.items()}
    recipients = recipients if isinstance(recipients, list) else [recipients]

    mail = EmailMultiAlternatives(
        from_email=f"{settings.EMAIL_NAME} <{settings.EMAIL_ADDRESS}>",
        subject=subject,
        body="",
        to=recipients
    )
    mail.template_id = template_id
    mail.substitutions = substitutions
    mail.alternatives = [(" ", "text/html")]

    if content:
        mail.attach_alternative(content, "text/html")

    mail.send()
    if logger:
        logger.info("Email sent to %s", recipients)
    return True


def render_email_body(template_name, context=None):
    """Generate text and HTML for an email body using the named email template,
    with substitutions provided by `context`.
    """
    context = {} if context is None else context
    html = render_to_string(f"email/{template_name}.djhtml", context)
    try:
        text = render_to_string(f"email/{template_name}.djtxt", context)
    except TemplateDoesNotExist:
        text = strip_tags(html)

    html = toronado.from_string(html).decode("utf-8")

    return (html, text)


def render_generic_body(template_name, context={}):
    """Prepare the context to be inserted into a generic SendGrid template by
    rendering the partial templates in templates/sendgrid, if present. The
    context will contain `message_html`, `message_text`, `footer_html`, and
    `footer_text` fields.

    """
    # In production, both valid templates -and- TemplateDoesNotExist exceptions
    # are cached, so the penalty here should be low.
    generic_context = {k: context[k] for k in ["message_html", "message_text",
                                               "footer_html", "footer_text"]
                       if k in context}
    if "message_html" not in context:
        generic_context["message_html"] = render_to_string(f"sendgrid/{template_name}_body.djhtml", context)
    if "message_text" not in context:
        try:
            generic_context["message_text"] = render_to_string(f"sendgrid/{template_name}_body.djtxt", context)
        except TemplateDoesNotExist:
            generic_context["message_text"] = strip_tags(generic_context["message_html"])

    unique_footer = False
    if "footer_html" not in context:
        try:
            generic_context["footer_html"] = render_to_string(f"sendgrid/{template_name}_footer.djhtml", context)
            unique_footer = True
        except TemplateDoesNotExist:
            generic_context["footer_html"] = render_to_string("sendgrid/footer.djhtml", context)
    if "footer_text" not in context:
        try:
            generic_context["footer_text"] = render_to_string(f"sendgrid/{template_name}_footer.djtxt", context)
        except TemplateDoesNotExist:
            if unique_footer:
                generic_context["footer_text"] = strip_tags(generic_context["footer_html"])
            else:
                generic_context["footer_text"] = render_to_string("sendgrid/footer.djtxt", context)

    return generic_context


def send_template(email, subject, template_name, context=None, logger=logger):
    """Construct and send an email with subject `subject` to `email`, using the
    named email template.
    """
    context = context or {}
    html, text = render_email_body(template_name, context)

    mail = EmailMultiAlternatives(
        from_email=f"{settings.EMAIL_NAME} <{settings.EMAIL_ADDRESS}>",
        subject=subject,
        body=text,
        to=(email if isinstance(email, list) else [email]))
    mail.attach_alternative(html, "text/html")
    mail.send()
    logger.info("Sent '%s' email to %s", template_name,
                email)
