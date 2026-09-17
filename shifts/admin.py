from django.contrib import admin

from .models import Shift


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("date", "site", "start_time", "end_time", "hourly_rate", "shift_type")
    list_filter = ("site__agency", "shift_type")
    date_hierarchy = "date"
