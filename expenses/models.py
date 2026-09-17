from django.conf import settings
from django.db import models

from agencies.models import Agency


class Expense(models.Model):
    class Category(models.TextChoices):
        UNIFORM = "UNIFORM", "Uniform"
        TRAVEL = "TRAVEL", "Travel"
        EQUIPMENT = "EQUIPMENT", "Equipment"
        OTHER = "OTHER", "Other"

    # Direct FK rather than deriving ownership from `agency`, since agency is
    # nullable - an unlinked expense still needs a clear, non-nullable owner.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="expenses_owned"
    )
    date = models.DateField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    agency = models.ForeignKey(
        Agency, on_delete=models.SET_NULL, null=True, blank=True, related_name="expenses"
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.get_category_display()} £{self.amount} on {self.date}"
