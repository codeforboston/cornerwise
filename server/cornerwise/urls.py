from django.conf.urls.static import static
from django.conf import settings
from django.urls import include, path

import user
from cornerwise.views import index

urlpatterns = [
    path("admin/", include("cornerwise.admin_urls")),
    path("parcel/", include("parcel.urls")),
    path("project/", include("project.urls")),
    path("proposal/", include("proposal.urls")),
    path("doc/", include("proposal.doc_urls")),
    path("task/", include("task.urls")),
    path("user/", include("user.urls")),
    path("contact", user.views.contact_us, name="contact-us"),
    path("tinymce/", include("tinymce.urls")),
    path("", index, name="front-page"),
]

if settings.SERVE_MEDIA:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.ENABLE_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls))
    ] + urlpatterns
