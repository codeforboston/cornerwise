from django.apps import AppConfig


class ParcelConfig(AppConfig):
    name = "parcel"

    def ready(self):
        from . import models

        try:
            models.LotSize.refresh()
        except:
            pass
