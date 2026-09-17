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
