from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from parcel.models import LotQuantiles


def get_lot_sizes():
    q = LotQuantiles.objects.all()[0]
    return {"small": round(q.small_lot * 43560),
            "medium": round(q.medium_lot * 43560)}

LOT_SIZES = get_lot_sizes()


@ensure_csrf_cookie
def index(request):
    return render(request, "index.djhtml",
                  {"google_key": settings.GOOGLE_BROWSER_API_KEY,
                   "production": settings.IS_PRODUCTION,
                   "lot_sizes": LOT_SIZES})
