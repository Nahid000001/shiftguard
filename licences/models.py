from django.conf import settings
from django.db import models
from django.utils import timezone


class Licence(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="licences")
    name = models.CharField(max_length=200)
    licence_number = models.CharField(max_length=100)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    reminder_days_before = models.PositiveIntegerField(default=60)

    class Meta:
        ordering = ["expiry_date"]

    def __str__(self):
        return f"{self.name} ({self.licence_number})"

    @property
    def days_until_expiry(self):
        # timezone.localdate(), not date.today() - the latter ignores
        # Django's configured TIME_ZONE entirely and uses the server OS
        # clock's timezone, which would silently miscalculate this on any
        # server not set to Europe/London (most cloud hosts default to UTC).
        return (self.expiry_date - timezone.localdate()).days

    @property
    def is_expired(self):
        return self.days_until_expiry < 0

    @property
    def is_expiring_soon(self):
        return 0 <= self.days_until_expiry <= self.reminder_days_before
