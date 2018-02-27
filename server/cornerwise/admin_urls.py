from django.conf.urls import include, url

from shared import admin_views, admin


urlpatterns = [
    url(r"^celery_log", admin_views.celery_logs),
    url(r"^", admin.cornerwise_admin.urls)
]
