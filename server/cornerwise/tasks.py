from django.conf import settings
import re
import sendgrid

from cornerwise import celery_app


if getattr(settings, "SENDGRID_API_KEY", None):
    SG = sendgrid.SendGridClient(settings.SENDGRID_API_KEY)
else:
    SG = None


@celery_app.task()
def send_subscription_updates(subscription, proposals):
    if SG:
        message = sendgrid.Mail()
        user = subscription.user
        if user:
            message.add_to("{first} {last} <{email}>".
                           format(first=user.first_name,
                                  last=user.last_name,
                                  email=user.email or subscription.email))
        else:
            message.add_to(subscription.email)

        message.set_subject("Cornerwise: Updates")
        message.set_html("")
        message.set_text("")
        message.set_from(settings.EMAIL_ADDRESS)

        status, msg = SG.send(message)


@celery_app.task()
def run_notifications():
    pass
