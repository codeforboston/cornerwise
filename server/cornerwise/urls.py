from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.views import static


from cornerwise.views import index, contact_us

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^parcel/', include("parcel.urls")),
    url(r'^project/', include("project.urls")),
    url(r'^proposal/', include("proposal.urls")),
    url(r"^doc/", include("proposal.doc_urls")),
    url(r"^task/", include("task.urls")),
    url(r"^user/", include("user.urls")),
    url(r"^contact$", contact_us, name="contact-us"),
    url(r"^$", index, name="front-page"),
]

if settings.SERVE_MEDIA:
    urlpatterns += [
        url(r"^" + settings.MEDIA_URL + "(?P<path>.*)$",
            static.serve, {"document_root": settings.MEDIA_ROOT}),
    ]

if settings.SERVE_STATIC:
    urlpatterns += [
        url(r"^" + settings.STATIC_URL + "(?P<path>.*)$",
            static.serve, {"document_root": settings.STATIC_ROOT}),
    ]
