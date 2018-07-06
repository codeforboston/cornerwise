import json

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from parcel.models import LotQuantiles
from proposal.models import Importer


def get_lot_sizes():
    return {
        town.town_id: {
            "small": round(town.small_lot * 43560),
            "medium": round(town.medium_lot * 43560)
        }
        for town in LotQuantiles.objects.all()
    }


LOT_SIZES = None


def lot_sizes(town_id):
    global LOT_SIZES
    if not LOT_SIZES:
        LOT_SIZES = get_lot_sizes()

    try:
        return LOT_SIZES[town_id]
    except KeyError:
        return {"small": 5000, "medium": 10000}


def last_updated(site_config=None):
    q = site_config.importer_query if site_config else {}
    last_run = Importer.objects.filter(last_run__isnull=False, **q)\
                               .values_list("last_run", flat=True)
    return max(last_run) if last_run else None


@ensure_csrf_cookie
def index(request):
    return render(request, "index.djhtml", {
        "google_key": settings.GOOGLE_BROWSER_API_KEY,
        "production": settings.IS_PRODUCTION,
        "lot_sizes": lot_sizes(request.site_config.town_id),
        "last_updated": last_updated(request.site_config),
        "preload_data": json.dumps({}),
        "js_filename": settings.JS_FILENAME,
        "css_filename": settings.CSS_FILENAME
    })
