from django.urls import path

from shared import admin_views, admin
from shared.staff_notifications import user_notification_form, send_user_notification
from shared.subscription_preview import subscription_preview


urlpatterns = [
    path("celery_log", admin_views.celery_logs, name="celery_log"),
    path("task_logs", admin_views.task_logs, name="task_logs"),
    path("task_failures", admin_views.task_failure_logs, name="task_failures"),
    path("task_stats", admin_views.task_stats, name="task_stats"),
    path("importer_errors", admin_views.importer_errors, name="importer_errors"),
    path("clear_importer_errors", admin_views.clear_importer_errors, name="clear_importer_errors"),
    path("recent_tasks", admin_views.recent_tasks, name="recent_tasks"),
    path("message", user_notification_form, name="notification_form"),
    path("send_notification", send_user_notification, name="send_notification"),
    path("preview_subscription", subscription_preview, name="preview-subscription"),
    path("refresh_parcels", admin_views.refresh_parcels, name="refresh_parcels"),
    path("", admin.cornerwise_admin.urls),
]
