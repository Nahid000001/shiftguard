from django.contrib import admin

from .models import Licence


@admin.register(Licence)
class LicenceAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "licence_number", "expiry_date", "is_expiring_soon")
    list_filter = ("name", "user")
