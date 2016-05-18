from django.contrib.auth import get_user_model
from . import tasks


# When email is sent to @cornerwise.org, SendGrid parses it and posts the
# reults to this view:
def mail_inbound(request):
    """
    See https://sendgrid.com/docs/API_Reference/Webhooks/parse.html for
    documentation of the POST fields.
    """
    try:
        email = request.POST["from"]
        User = get_user_model()
        user = User.objects.get(email=email)
        lines = request.POST["text"].split("\n")
        for line in lines:
            command = line.strip().split(" ")[0]
            if command in email_commands:
                email_commands(command, request, user)
                return
    except (KeyError, User.DoesNotExist):
        return


def deactivate_account(request, user):
    user.profile.deactivate()
    tasks.send_deactivation_email.delay(user)


def reset_account(request, user):
    user.profile.generate_token()
    tasks.send_reset_email.delay(user)


email_commands = {
    "deactivate": deactivate_account,
    "reset": reset_account
}
