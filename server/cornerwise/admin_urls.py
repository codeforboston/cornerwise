from django.urls import path

from shared import admin_views, admin


urlpatterns = [
    path("celery_log", admin_views.celery_logs, name="celery_log"),
    path("task_logs", admin_views.task_logs, name="task_logs"),
    path("task_failures", admin_views.task_failure_logs, name="task_failures"),
    path("recent_tasks", admin_views.recent_tasks, name="recent_tasks"),
    path("message", admin_views.user_notification_form, name="send_message"),
    path("", admin.cornerwise_admin.urls)
]
