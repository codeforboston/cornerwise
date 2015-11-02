from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^find$", views.find_parcels,),
    url(r"^loc_id/(F_[\d_]+)$", views.parcel_with_loc_id),
]
