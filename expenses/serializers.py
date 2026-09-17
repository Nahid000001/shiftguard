from rest_framework import serializers

from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    agency_name = serializers.CharField(source="agency.name", read_only=True, default=None)

    class Meta:
        model = Expense
        fields = ["id", "date", "category", "amount", "agency", "agency_name", "notes"]
