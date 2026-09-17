from rest_framework import serializers

from .models import Licence


class LicenceSerializer(serializers.ModelSerializer):
    days_until_expiry = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    is_expiring_soon = serializers.ReadOnlyField()

    class Meta:
        model = Licence
        fields = [
            "id",
            "name",
            "licence_number",
            "issue_date",
            "expiry_date",
            "reminder_days_before",
            "days_until_expiry",
            "is_expired",
            "is_expiring_soon",
        ]
