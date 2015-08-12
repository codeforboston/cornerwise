from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"at_point", views.parcels_at_point,)
]
