from django.contrib import admin

from .models import Agency, Site


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "employment_type")
    list_filter = ("employment_type", "user")


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "agency", "default_hourly_rate")
    list_filter = ("agency",)
