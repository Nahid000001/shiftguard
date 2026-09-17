from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("tax-summary/", views.TaxSummaryView.as_view(), name="tax-summary"),
    path("tax-summary/export.csv", views.TaxSummaryCSVView.as_view(), name="tax-summary-csv"),
    path("tax-summary/export.pdf", views.TaxSummaryPDFView.as_view(), name="tax-summary-pdf"),
]
