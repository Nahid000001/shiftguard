from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services import build_tax_summary
from .utils import parse_start_year, tax_year_label


@api_view(["GET"])
def tax_summary_api(request):
    start_year = parse_start_year(request)
    summary = build_tax_summary(request.user, start_year)
    summary["prev_year"] = start_year - 1
    summary["prev_label"] = tax_year_label(start_year - 1)
    summary["next_year"] = start_year + 1
    summary["next_label"] = tax_year_label(start_year + 1)
    return Response(summary)
