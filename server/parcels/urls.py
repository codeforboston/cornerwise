from django.conf.urls import url

import citydash.parcels.views as views

urlpatterns = [
    url(r"at_point", views.at_point,)
]
