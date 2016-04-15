from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^manage", views.manage),
    url(r"^delete_subscription/(?P<sub_id>\d+)", views.delete_subscription),
    url(r"^delete_subscriptions", views.delete_subscriptions),
    url(r"^deactivate", views.deactivate_account),
    url(r"^activate", views.activate_account),
    url(r"^(?P<token>[a-zA-Z0-9\-]+)/(?P<pk>\d+)/", views.login,
        name="user-login"),
    url(r"^subscribe", views.subscribe
]
