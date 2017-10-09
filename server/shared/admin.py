from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.gis.admin import GeoModelAdmin

from proposal.models import Importer, Layer

from utils import geometry_from_url


class CornerwiseAdmin(admin.AdminSite):
    site_header = "Cornerwise"


class ImporterForm(forms.ModelForm):
    timezone = forms.ChoiceField(choices=[("US/Eastern", "Eastern"),
                                          ("US/Central", "Central"),
                                          ("US/Mountain", "Mountain"),
                                          ("US/Pacific", "Pacific")])
    class Meta:
        model = Importer
        exclude = ["last_run"]


class ImporterAdmin(admin.ModelAdmin):
    model = Importer
    form = ImporterForm


class LayerForm(forms.ModelForm):
    auto_calculate_envelope = forms.BooleanField(
        initial=True,
        help_text="""If True, the geometry envelope will be calculated
        automatically from the contents of the GeoJSON.
        """)

    class Meta:
        model = Layer
        fields = "__all__"

    def save(self, commit=True):
        m = super().save(commit=False)

        if self.fields["auto_calculate_envelope"]:
            gc = geometry_from_url(self.fields["url"])
            # TODO Add a buffer to the envelope? (gc.envelope.buffer)
            m.envelope = gc.envelope

        if commit:
            m.save()
        return m


class LayerAdmin(GeoModelAdmin):
    default_lat = 42.387545768736246
    default_lon = -71.14565849304199

    form = LayerForm


cornerwise_admin = CornerwiseAdmin(name="admin")

cornerwise_admin.register(Importer, ImporterAdmin)
cornerwise_admin.register(Layer, LayerAdmin)
cornerwise_admin.register(User, UserAdmin)
