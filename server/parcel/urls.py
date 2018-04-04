from django.urls import path, re_path

from . import views


app_name = "parcels"
urlpatterns = [
    path(r"find", views.find_parcels, name="find"),
    re_path(r"^loc_id/(F_[\d_]+)$", views.parcel_with_loc_id,
            name="lookup-by-loc"),
]
