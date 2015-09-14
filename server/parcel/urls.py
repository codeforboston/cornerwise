from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^at_point$", views.parcel_at_point,),
    url(r"^at_points$", views.parcels_at_points),
    url(r"^loc_id/(F_[\d_]+)$", views.parcel_with_loc_id),
]
