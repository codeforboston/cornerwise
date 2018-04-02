from django.conf.urls import url

from shared import admin_views, admin


urlpatterns = [
    url(r"^celery_log", admin_views.celery_logs, name="celery_log"),
    url(r"^task_logs", admin_views.task_logs, name="task_logs"),
    url(r"^task_failures", admin_views.task_failure_logs, name="task_failures"),
    url(r"^recent_tasks", admin_views.recent_tasks, name="recent_tasks"),
    url(r"^message", admin_views.user_notification_form, name="send_message"),
    url(r"^", admin.cornerwise_admin.urls)
]
