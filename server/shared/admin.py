"""Cornerwise admin configuration

Allow administrators to configure proposal, case, and project importers.

"""
from datetime import datetime, timedelta
from functools import reduce

from django.contrib import admin, messages
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.contrib.gis.admin import GeoModelAdmin
from django.contrib.gis import forms
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.formats import date_format

from proposal.models import Attribute, Changeset, Event, Importer, Layer, Proposal
from .models import StaffNotification
from user.models import UserComment

import redis_utils as red
from utils import geometry_from_url

import jsonschema


User = get_user_model()


class AttributeInline(admin.StackedInline):
    extra = 1
    fields = ["name", "hidden", "ignore_updates", "text_value", "date_value", "record_change"]
    model = Attribute

    class form(forms.ModelForm):
        record_change = forms.BooleanField(initial=True)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["text_value"].widget.attrs["rows"] = 2
            self.fields["text_value"].required = False
            self.fields["date_value"].required = False
            if getattr(self, "instance", None) and self.instance.pk:
                self.fields["name"].disabled = True
            else:
                self.fields["record_change"].widget = forms.HiddenInput()

        def is_valid(self):
            print(self.instance, self.instance.text_value)
            result = super().is_valid()
            print(self.instance, self.instance.text_value)
            return result


class ProposalAdmin(admin.ModelAdmin):
    fields = ["case_number", "address", "updated"]
    search_fields = ["case_number", "address"]

    inlines = [AttributeInline]

    class Meta:
        model = Proposal

    class form(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if getattr(self, "instance"):
                self.fields["case_number"].disabled = False

    def save_related(self, request, form, formsets, change):
        if change:
            changed_attrs = [attr_form.instance for attr_form in formsets[0]
                            if attr_form.changed_data]
            pks = [attr.pk for attr in changed_attrs if attr.pk]
            old_attrs = {at.handle: at for at in Attribute.objects.filter(pk__in=pks)}

        super().save_related(request, form, formsets, change)
        if not change:
            return

        changed = [a[0] for a in formsets[0].changed_objects]
        changes = [{"name": attr.name,
                    "new": attr.text_value or attr.date_value,
                    "old": old and (old.text_value or old.date_value)}
                   for attr, old in zip(changed, (old_attrs.get(a.handle) for a in changed))]

        Changeset.from_changes(form.instance, {
            "attributes": [ch for ch in changes if ch["old"] != ch["new"]],
            "properties": []
        }).save()


class CornerwiseAdmin(admin.AdminSite):
    site_header = "Cornerwise"

    def get_urls(self):
        from django.urls import path

        def autocomplete_view(request):
            return self.admin_view(
                AutocompleteJsonView.as_view(
                    model_admin=ProposalAdmin(Proposal, self)))(request)

        return super().get_urls() + [
            path("autocomplete/proposal",
                 autocomplete_view,
                 name="proposal_proposal_autocomplete")
        ]


class ImporterForm(forms.ModelForm):
    timezone = forms.ChoiceField(choices=[("US/Eastern", "Eastern"),
                                          ("US/Central", "Central"),
                                          ("US/Mountain", "Mountain"),
                                          ("US/Pacific", "Pacific")])
    class Meta:
        exclude = ["last_run"]
        model = Importer


def run_importers(_modeladmin, request, importers):
    from proposal import tasks

    pks = list(importers.values_list("pk", flat=True))
    res = tasks.pull_updates.delay(None, {"pk__in": pks})
    n = len(pks)
    s, p = (" is", "its") if n == 1 else ("s are", "their")

    messages.info(
        request, (f"The importer{s} now running in the background. "
                  f"Refresh this page to monitor {p} progress."))

    return redirect(reverse("task_logs")  + f"?task_id={res.task_id}")


def validate_importers(_, request, importers):
    when = datetime.now() - timedelta(days=30)
    for importer in importers:
        data = importer.updated_since(when)
        try:
            importer.validate(data)
        except jsonschema.exceptions.ValidationError as err:
            schema_path = "/".join(map(str, err.absolute_schema_path))
            messages.warning(
                request,
                f"Validation error for {importer} "
                f"at {schema_path}: {err.message}")
            messages.warning(
                request,
                str(reduce(lambda d, k: d[k], err.absolute_path, data)),
            )
        else:
            messages.info(request, f"{importer} successfully validated!")


def view_import_errors(_, request, importers):
    return redirect("{}?{}".format(reverse("importer_errors"),
                                   "&".join(f"importer={imp.pk}" for imp in importers)))


def clear_import_errors(_, request, importers):
    red.Redis.delete([
        f"cornerwise:importer:{importer.pk}:import_errors"
        for importer in importers
    ])


class ImporterAdmin(admin.ModelAdmin):
    model = Importer
    form = ImporterForm
    actions = [run_importers, validate_importers, view_import_errors,
               clear_import_errors]
    readonly_fields = ["last_run_date"]

    def last_run_date(self, importer):
        if importer.last_run:
            return date_format(importer.last_run)

        return mark_safe("<em>Never run</em>")


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


class ReadOnlyAdmin(admin.ModelAdmin):
    def __init__(self, *args, exclude=[], **kwargs):
        super().__init__(*args, **kwargs)
        self.exclude = exclude
        self.readonly_fields = [f.name for f in self.model._meta.get_fields()
                                if f.name not in exclude]
        # self.readonly_fields += ["message_text"]

    # exclude = ("message",)

    # def message_text(self, notification):
    #     return mark_safe(notification.message)

    def proposals(self, notification):
        pks = notification.proposals.split(",")
        proplist = ", ".join([str(proposal) for proposal in
                              Proposal.objects.filter(pk__in=pks)])
        return mark_safe(proplist)


cornerwise_admin = CornerwiseAdmin(name="admin")

cornerwise_admin.register(Proposal, ProposalAdmin)
cornerwise_admin.register(Importer, ImporterAdmin)
cornerwise_admin.register(Layer, LayerAdmin)
cornerwise_admin.register(User, UserAdmin)
cornerwise_admin.register(UserComment, ReadOnlyAdmin)
cornerwise_admin.register(Group, GroupAdmin)
cornerwise_admin.register(Event, admin.ModelAdmin)
cornerwise_admin.register(StaffNotification, ReadOnlyAdmin)
