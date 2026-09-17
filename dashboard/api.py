from rest_framework.decorators import api_view
from rest_framework.response import Response

from licences.serializers import LicenceSerializer
from shifts.serializers import ShiftSerializer

from .services import build_charts_data, build_dashboard_summary


@api_view(["GET"])
def dashboard_summary_api(request):
    summary = build_dashboard_summary()
    return Response(
        {
            "week_start": summary["week_start"],
            "week_end": summary["week_end"],
            "week_shifts": ShiftSerializer(summary["week_shifts"], many=True).data,
            "week_total": summary["week_total"],
            "month_total": summary["month_total"],
            "upcoming_expiries": LicenceSerializer(summary["upcoming_expiries"], many=True).data,
        }
    )


@api_view(["GET"])
def charts_data_api(request):
    return Response(build_charts_data())
