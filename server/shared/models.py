from django.contrib.gis.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Actions(models.Model):
    class Meta:
        managed = False

        permissions = (
            ("send_notifications", "Can send notifications to users"),
            ("view_debug_logs", "Can view celery debugging logs"),
        )


class StaffNotification(models.Model):
    title = models.CharField(max_length=100)
    sender = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    points = models.MultiPointField(null=True)
    addresses = models.TextField(blank=True, default="")
    proposals = models.TextField(blank=True, default="")
    radius = models.FloatField()
    message = models.TextField()
    subscribers = models.IntegerField()
    region = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.sender}: {self.title}"
