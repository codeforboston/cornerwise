from django.conf import settings
from django.shortcuts import render
from django.template import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def index(request):
    d = { "google_key": settings.GOOGLE_BROWSER_API_KEY,
          "app_mode": settings.APP_MODE }
    return render(request, "index.djhtml",
                  context=RequestContext(request, d))
