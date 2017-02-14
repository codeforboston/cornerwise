from shared import mail

def send(user, subject, template_name, context=None, content=None):
    """
    Send an email to a user. If there is a SendGrid template id configured for
    the given template name, create substitutions from `context` so that `-key`
    in the template is replaced by the value of `key` in `context`.

    If there is no such SendGrid template, falls back to using a Django
    template in <templates>/email.
    """
    context = context or {}
    context["user"] = user.profile.addressal
    context["unsubscribe_url"] = user.profile.unsubscribe_url

    return mail.send(user.email, subject, template_name, context)
