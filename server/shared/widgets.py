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
        return [distance.ft, "ft"]


class DistanceField(MultiValueField):
    widget = DistanceWidget

    DISTANCE_UNITS = [("ft", "feet"),
                      ("m", "meters"),
                      ("km", "km"),
                      ("mi", "miles")]

    def __init__(self, *args, min_value=10, max_value=100, initial_unit="ft",
                 **kwargs):
        error_messages = {
            "incomplete": "Enter a distance"
        }
        fields = (
            FloatField(min_value=min_value, max_value=max_value,),
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

    def compress(self, values):
        return D(**{values[1]: values[0]})
