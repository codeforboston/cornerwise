import json

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from parcel.models import LotQuantiles

from .contact import ContactForm


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


def contact_us(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.send_email()
            return JsonResponse({
                "title": "Email Sent",
                "text": "Thanks for your feedback!"
            })
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    else:
        return HttpResponse({
            "bad request method"
        }, status=405)


@ensure_csrf_cookie
def index(request):
    return render(request, "index.djhtml", {
        "google_key": settings.GOOGLE_BROWSER_API_KEY,
        "production": settings.IS_PRODUCTION,
        "lot_sizes": lot_sizes(),
        "preload_data": json.dumps({}),
        "js_filename": settings.JS_FILENAME,
        "css_filename": settings.CSS_FILENAME
    })
