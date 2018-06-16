from django import forms
from django.conf import settings

from django.contrib.auth import get_user_model

from shared import mail
from .models import UserComment
from .utils import admin_emails, group_emails


User = get_user_model()


class ContactForm(forms.Form):
    send_to = forms.ChoiceField(label="Contact")
    subject = forms.CharField(label="Subject", max_length=100, required=False, initial="")
    comment = forms.CharField(
        label="Comments",
        max_length=1000,
        min_length=50,
        widget=forms.Textarea)

    def __init__(self, data=None, request=None, **kwargs):
        super().__init__(data or (request and request.POST), **kwargs)
        self.request = request
        self.model = None

        send_to = self.fields["send_to"]
        send_to.choices = [(c["name"], c["topic"]) for c in request.site_config.contacts]

    def clean(self):
        cleaned = super().clean()

        request = self.request
        cleaned.update({
            "user": request.user if request.user.is_authenticated else None,
            "remote_addr": request.META["REMOTE_ADDR"],
            "remote_host": request.META["REMOTE_HOST"],
            "site_name": request.site_config.hostname,
        })

        return cleaned

    def save(self):
        if not self.model:
            self.model = UserComment.objects.create(**self.cleaned_data)
        return self.model

    def send_email(self):
        cleaned = self.cleaned_data
        contact = self.request.site_config.contact_for_name(cleaned["send_to"])
        emails = []
        if contact:
            if "email" in contact:
                emails = [contact["email"]]
            elif "group" in contact:
                emails = group_emails[contact["group"]]

        if not emails:
            emails = group_emails(self.request.site_config.group_name) or \
                admin_emails()

        if emails:
            for email in emails:
                mail.send(email, "Cornerwise: User Feedback", "user_feedback",
                          cleaned)
            return True
