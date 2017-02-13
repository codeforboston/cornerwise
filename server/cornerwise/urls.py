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
from django.views.static import serve as static_serve


from cornerwise.views import index

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^parcel/', include("parcel.urls")),
    url(r'^project/', include("project.urls")),
    url(r'^proposal/', include("proposal.urls")),
    url(r"^doc/", include("proposal.doc_urls")),
    url(r"^task/", include("task.urls")),
    url(r"^user/", include("user.urls")),
    url(r"^$", index, name="front-page"),
]

if settings.SERVE_MEDIA:
    urlpatterns += [
        url(r"^" + settings.MEDIA_URL + "(?P<path>.*)$",
            static_serve, {"document_root": settings.MEDIA_ROOT}),
    ]

if settings.SERVE_STATIC:
    urlpatterns += [
        url(r"^" + settings.STATIC_URL + "(?P<path>.*)$",
            static_serve, {"document_root": settings.STATIC_ROOT}),
    ]
