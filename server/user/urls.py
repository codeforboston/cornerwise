from django.urls import path, re_path

from . import views
from .mail_parse_views import mail_inbound

urlpatterns = [
    path("confirm", views.confirm, name="confirm"),
    re_path("(?P<token>[a-zA-Z0-9\-/+=]+)/(?P<pk>\d+)/",
            views.user_login, name="user-login"),
    path("logout", views.user_logout, name="logout"),
    path("subscribe", views.subscribe, name="subscribe"),
    path("resend", views.resend_email, name="resend-confirmation"),
    path("changelog/", views.change_log, name="view-change-log"),
    path("deactivate", views.deactivate_account, name="deactivate-account"),
    path("activate", views.activate_account, name="activate-account"),

    # Parse incoming mail:
    path("mail_inbound", mail_inbound),


    path("manage", views.manage, name="manage-user"),
    # path("delete_subscriptions", views.delete_subscriptions),
    path("delete_subscription", views.delete_subscription, name="delete-subscription"),
    path("activate_subscription", views.activate_subscription, name="activate-subscription"),
    path("deactivate_subscription", views.deactivate_subscription, name="deactivate-subscription"),
    path("changes/", views.change_summary, name="view-subscription-changes"),
]
