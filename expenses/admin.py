from django.contrib import admin

from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "category", "amount", "agency")
    list_filter = ("category", "agency", "user")
    date_hierarchy = "date"
