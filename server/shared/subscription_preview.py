from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import render

from django.contrib.admin import widgets as admin_widgets
from django.contrib.auth.decorators import user_passes_test
from django.contrib.gis import forms
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.forms.widgets import OSMWidget

from user.models import Subscription
from user.mail import updates_context

from .admin import cornerwise_admin
from .geocoder import Geocoder
from .mail import render_email_body
from .widgets import DistanceWidget, DistanceField


is_superuser = user_passes_test(lambda user: user.is_superuser, "/admin")

def js_files():
    extra = '' if settings.DEBUG else '.min'
    return [f"admin/js/{path}" for path in [ f'vendor/jquery/jquery{extra}.js',
                                             'jquery.init.js',
                                             'core.js',
                                             'admin/RelatedObjectLookups.js',
                                             f'actions{extra}.js',
                                             'urlify.js',
                                             f'prepopulate{extra}.js',
                                             f'vendor/xregexp/xregexp{extra}.js',]]


class SubscriptionPreviewForm(forms.Form):
    center = forms.PointField(help_text="With the radius, determines the notification area.",
                              srid=4326)
    radius = DistanceField(
        min_value=D(ft=100), max_value=D(mi=1), initial=D(ft=300))
    region_name = forms.ChoiceField(choices=(("Somerville, MA", "Somerville, MA"),),
                                    initial=settings.GEO_REGION)
    start = forms.DateTimeField(widget=admin_widgets.AdminDateWidget(),
                                help_text="Find changes since this date")
    end = forms.DateTimeField(widget=admin_widgets.AdminDateWidget(),
                              help_text="Find changes up to this date")

    class Media:
        js = js_files()

    def clean(self):
        cleaned = super().clean()

        if cleaned["start"] >= cleaned["end"]:
            self.add_error("start", ValidationError("start should be less than end"))
            self.add_error("end", ValidationError("end should be greater than start"))

        try:
            center = cleaned["center"]
            cleaned["address"] = Geocoder.reverse_geocode(center.y, center.x).split(",")[0]
        except:
            cleaned["address"] = None

        return cleaned


@is_superuser
def subscription_preview(request):
    context = cornerwise_admin.each_context(request).copy()

    if request.method == "POST":
        form = SubscriptionPreviewForm(request.POST)

        if form.is_valid():
            return render_changelog(request, form.cleaned_data)
    else:
        form = SubscriptionPreviewForm()

    if request.site_config and request.site_config.region_name:
        point = request.site_config.center
        form.fields["center"].widget = OSMWidget(attrs={"default_lat": point.y,
                                                        "default_lon": point.x,
                                                        "default_zoom": 14})
        form.fields["region_name"].initial = request.site_config.region_name

    context["form"] = form
    context["title"] = "Preview Subscription Changes"
    return render(request, "admin/preview_subscription_form.djhtml", context)


def render_changelog(request, data):
    context = cornerwise_admin.each_context(request)
    context["title"] = "Preview Subscription Changes"
    sub = Subscription(created=data["start"],
                       updated=data["start"],
                       center=data["center"],
                       radius=data["radius"].m,
                       address=data["address"],
                       region_name=data["region_name"])

    context.update(updates_context(sub, sub.summarize_updates(data["start"])))
    return render(request, "admin/preview_subscription.djhtml", context)
