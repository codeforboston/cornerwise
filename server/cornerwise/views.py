import json

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from shared import mail

from parcel.models import LotQuantiles


def get_lot_sizes():
    try:
        q = LotQuantiles.objects.all()[0]
        return {
            "small": round(q.small_lot * 43560),
            "medium": round(q.medium_lot * 43560)
        }
    except IndexError:
        return {"small": 5000, "medium": 10000}


LOT_SIZES = None


def lot_sizes():
    global LOT_SIZES
    if not LOT_SIZES:
        LOT_SIZES = get_lot_sizes()
    return LOT_SIZES


RECIPIENTS = {
    "planning-board": "someone",
    "cornerwise": "admin@cornerwise.org",
    "webmaster": "dan@cornerwise.org"
}


def contact_us(request):
    if request.method == "GET":
        return render(request, "contact.djhtml")

    message = request.POST["comment"]
    recipient = request.POST["send_to"]

    if recipient in RECIPIENTS:
        email = RECIPIENTS[recipient]
        mail.send(email, "Cornerwise: Feedback", "feedback",
                  {"comment": message})
        return


@ensure_csrf_cookie
def index(request):
    return render(request, "index.djhtml", {
        "google_key": settings.GOOGLE_BROWSER_API_KEY,
        "production": settings.IS_PRODUCTION,
        "lot_sizes": lot_sizes(),
        "preload_data": json.dumps({})
    })
