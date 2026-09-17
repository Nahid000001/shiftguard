from rest_framework import serializers

from .models import Shift


class ShiftSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source="site.name", read_only=True)
    agency_name = serializers.CharField(source="site.agency.name", read_only=True)
    duration_hours = serializers.ReadOnlyField()
    calculated_pay = serializers.ReadOnlyField()

    class Meta:
        model = Shift
        fields = [
            "id",
            "site",
            "site_name",
            "agency_name",
            "date",
            "start_time",
            "end_time",
            "hourly_rate",
            "shift_type",
            "notes",
            "duration_hours",
            "calculated_pay",
        ]

    def validate_site(self, site):
        request = self.context["request"]
        if site.agency.user_id != request.user.id:
            raise serializers.ValidationError("Not one of your sites.")
        return site
