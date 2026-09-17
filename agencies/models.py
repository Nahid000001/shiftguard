from django.conf import settings
from django.db import models


class Agency(models.Model):
    class EmploymentType(models.TextChoices):
        PAYE = "PAYE", "PAYE"
        SELF_EMPLOYED = "SELF_EMPLOYED", "Self-employed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agencies")
    name = models.CharField(max_length=200)
    employment_type = models.CharField(
        max_length=20, choices=EmploymentType.choices, default=EmploymentType.PAYE
    )
    contact_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "agencies"

    def __str__(self):
        return self.name


class Site(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name="sites")
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300, blank=True)
    default_hourly_rate = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )

    class Meta:
        ordering = ["agency__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.agency.name})"
