from shared import mail
from cornerwise.utils import make_absolute_url


def _make_user_context(user, context):
    context = context.copy() if context else {}
    context["user"] = user.profile.addressal
    context["unsubscribe_url"] = make_absolute_url(user.profile.unsubscribe_url)
    return context


def send(user, subject, template_name, context=None, content=None):
    """
    Send an email to a user. If there is a SendGrid template id configured for
    the given template name, create substitutions from `context` so that `-key`
    in the template is replaced by the value of `key` in `context`.

    If there is no such SendGrid template, falls back to using a Django
    template in <templates>/email.
    """

    return mail.send(user.email, subject, template_name,
                     _make_user_context(user, context))
