from datetime import datetime, timedelta
from decimal import Decimal

from django.db import models

from agencies.models import Site


class Shift(models.Model):
    class ShiftType(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        OVERTIME = "OVERTIME", "Overtime"
        NIGHT = "NIGHT", "Night"
        BANK_HOLIDAY = "BANK_HOLIDAY", "Bank holiday"

    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="shifts")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    shift_type = models.CharField(
        max_length=20, choices=ShiftType.choices, default=ShiftType.STANDARD
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date", "-start_time"]

    def __str__(self):
        return f"{self.site.name} on {self.date}"

    @property
    def duration_hours(self):
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        if end <= start:
            end += timedelta(days=1)
        return Decimal((end - start).total_seconds()) / Decimal(3600)

    @property
    def calculated_pay(self):
        return (self.duration_hours * self.hourly_rate).quantize(Decimal("0.01"))
