from rest_framework import serializers

from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    agency_name = serializers.CharField(source="agency.name", read_only=True, default=None)

    class Meta:
        model = Expense
        fields = ["id", "date", "category", "amount", "agency", "agency_name", "notes"]

    def validate_agency(self, agency):
        if agency is None:
            return agency
        request = self.context["request"]
        if agency.user_id != request.user.id:
            raise serializers.ValidationError("Not one of your agencies.")
        return agency
