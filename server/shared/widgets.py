from django.core.exceptions import ValidationError
from django.forms.fields import FloatField, MultiValueField, ChoiceField
from django.forms.widgets import MultiWidget, NumberInput, Select

from django.contrib.gis.measure import D


class DistanceWidget(MultiWidget):
    def __init__(self, *args, choices=[], **kwargs):
        child_widgets = (
            NumberInput(),
            Select(choices=choices)
        )
        super().__init__(child_widgets, *args, **kwargs)

    def decompress(self, distance):
        if not isinstance(distance, D):
            distance = D(ft=distance)
        return [distance.ft, distance._default_unit]


class DistanceField(MultiValueField):
    widget = DistanceWidget

    DISTANCE_UNITS = [("ft", "feet"),
                      ("m", "meters"),
                      ("km", "km"),
                      ("mi", "miles")]

    def __init__(self, *args, min_value=D(m=10), max_value=D(m=100),
                 initial_unit="ft", **kwargs):
        error_messages = {
            "incomplete": "Enter a distance"
        }
        self.min_value = min_value
        self.max_value = max_value
        fields = (
            FloatField(),
            ChoiceField(choices=self.DISTANCE_UNITS,
                        initial=initial_unit)
        )
        super().__init__(
            fields=fields,
            error_messages=error_messages,
            require_all_fields=True,
            *args, **kwargs
        )
        self.widget = DistanceWidget(choices=self.DISTANCE_UNITS)

    def clean(self, val):
        val = super().clean(val)
        if self.min_value and val < self.min_value:
            unit = val._default_unit
            min_as_unit = getattr(self.min_value, unit)
            raise ValidationError(f"must be at least {min_as_unit} {unit}")
        elif self.max_value and val > self.max_value:
            unit = val._default_unit
            max_as_unit = getattr(self.max_value, unit)
            raise ValidationError(f"must be no more than {max_as_unit} {unit}")

        return val

    def compress(self, values):
        return D(**{values[1]: values[0]})
