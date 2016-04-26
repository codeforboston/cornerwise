from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^manage", views.manage, name="manage-user"),
    url(r"^delete_subscription/(?P<sub_id>\d+)", views.delete_subscription,
        name="delete-subscription"),
    # url(r"^delete_subscriptions", views.delete_subscriptions),
    url(r"^deactivate", views.deactivate_account,
        name="deactivate-account"),
    url(r"^activate", views.activate_account, name="activate-account"),
    url(r"^(?P<token>[a-zA-Z0-9\-+=]+)/(?P<pk>\d+)/", views.user_login,
        name="user-login"),
    url(r"^logout", views.user_logout, name="logout"),
    url(r"^subscribe", views.subscribe, name="subscribe"),
]
