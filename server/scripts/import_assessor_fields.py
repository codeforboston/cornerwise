import csv
import logging
import os

from django.db import IntegrityError

from parcel.models import Parcel, Attribute

logger = logging.getLogger(__name__)

def do_nothing(_parcel, _value):
    pass

# Use this to define field-specific handlers. Should map strings (field
# name as it occurs in assessor_data.csv) to functions, which should
# accept a Parcel and the raw value of the field.
known_field_handler = {
    "LOC_ID": do_nothing
}

def do_main(path="/data/assessor_data.csv"):
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            loc_id = row["LOC_ID"]
            try:
                parcel = Parcel.objects.filter(loc_id=loc_id)[0]

                for field, value in row.items():
                    handler = known_field_handler.get(field)

                    if handler:
                        handler(parcel, value)
                    else:
                        attribute = Attribute(parcel=parcel,
                                          name=field,
                                          value=value)
                        attribute.save()
            except IntegrityError as err:
                pass

            except IndexError as err:
                # No such Parcel exists
                logger.warn("No parcel exists with loc_id '%s'", loc_id)


if __name__ == "__main__":
    do_main()
