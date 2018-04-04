from django.db import models


class Actions(models.Model):
    class Meta:
        managed = False

        permissions = (
            ("send_notifications", "Can send notifications to users"),
            ("view_debug_logs", "Can view celery debugging logs"),
        )
