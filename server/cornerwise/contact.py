from django import forms
from django.conf import settings

from shared import mail

RECIPIENTS = {
    "planning-board": "admin@cornerwise.org",
    "cornerwise": "admin@cornerwise.org",
    "webmaster": "dan@cornerwise.org"
}


class ContactForm(forms.Form):
    send_to = forms.ChoiceField(
        choices=[("planning-board", "About a project"),
                 ("cornerwise", "About Cornerwise"), ("webmaster", "Other")],
        label="Contact")
    subject = forms.CharField(
        label="Subject",
        max_length=100)
    comment = forms.CharField(
        label="Comments",
        max_length=1000,
        min_length=50,
        widget=forms.Textarea)

    def send_email(self):
        send_to = self.cleaned_data["send_to"]
        email = RECIPIENTS[form_data["send_to"]]
        mail.send(email, "Cornerwise: User Feedback", "user_feedback",
                  {"text": self.comment,
                   "subject": self.subject})
