from rest_framework import serializers

from .models import Agency, Site


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ["id", "name", "employment_type", "contact_notes"]


class SiteSerializer(serializers.ModelSerializer):
    agency_name = serializers.CharField(source="agency.name", read_only=True)

    class Meta:
        model = Site
        fields = ["id", "agency", "agency_name", "name", "address", "default_hourly_rate"]

    def validate_agency(self, agency):
        request = self.context["request"]
        if agency.user_id != request.user.id:
            raise serializers.ValidationError("Not one of your agencies.")
        return agency
