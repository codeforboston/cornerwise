from django.conf.urls import url
from . import views
from .mail_parse_views import mail_inbound

urlpatterns = [
    url(r"^delete_subscription/(?P<sub_id>\d+)", views.delete_subscription,
        name="delete-subscription"),
    # url(r"^delete_subscriptions", views.delete_subscriptions),
    url(r"^deactivate$", views.deactivate_account, name="deactivate-account"),
    url(r"^activate$", views.activate_account, name="activate-account"),
    url(r"^(?P<token>[a-zA-Z0-9\-/+=]+)/(?P<pk>\d+)/", views.user_login,
        name="user-login"),
    url(r"^logout$", views.user_logout, name="logout"),
    url(r"^subscribe$", views.subscribe, name="subscribe"),
    url(r"^resend$", views.resend_email, name="resend-confirmation"),
    url(r"^changes/$", views.change_summary),
    url(r"^changes/(?P<sub_id>\d+)/$", views.change_summary,
        name="view-subscription-changes"),

    # Parse incoming mail:
    url(r"^mail_inbound$", mail_inbound),
    url(r"^manage$", views.manage, name="manage-user"),
    url(r"^$", views.default_view),
]
