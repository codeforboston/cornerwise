from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def index(request):
    return render(request, "index.djhtml",
                  {"google_key": settings.GOOGLE_BROWSER_API_KEY,
                   "app_mode": settings.APP_MODE})
