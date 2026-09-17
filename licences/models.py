from datetime import date

from django.db import models


class Licence(models.Model):
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
        return (self.expiry_date - date.today()).days

    @property
    def is_expired(self):
        return self.days_until_expiry < 0

    @property
    def is_expiring_soon(self):
        return 0 <= self.days_until_expiry <= self.reminder_days_before
