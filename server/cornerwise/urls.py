"""cornerwise URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse

import parcel.urls as parcel_urls
import project.urls as project_urls
import proposal.urls as proposal_urls
from proposal import doc_urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^parcel/', include(parcel_urls)),
    url(r'^project/', include(project_urls)),
    url(r'^proposal/', include(proposal_urls)),
    url(r"^doc/", include(doc_urls)),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^' + settings.STATIC_URL + '(?P<path>.*)$', "django.views.static.serve", {
            "document_root": settings.STATIC_ROOT
        }),
        url(r'^' + settings.MEDIA_URL + '(?P<path>.*)$', "django.views.static.serve", {
            "document_root": settings.MEDIA_ROOT
        }),
        url(r'^$', "django.views.static.serve", {
            "document_root": settings.STATIC_ROOT,
            "path": "index.html"
        }),
    ]
