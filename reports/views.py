import csv

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView

from .services import build_tax_summary
from .utils import tax_year_label, tax_year_start_year


def _requested_start_year(request):
    year = request.GET.get("year")
    if year and year.isdigit():
        return int(year)
    return tax_year_start_year()


class TaxSummaryView(LoginRequiredMixin, TemplateView):
    template_name = "reports/tax_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_year = _requested_start_year(self.request)
        context["summary"] = build_tax_summary(start_year)
        context["prev_year"] = start_year - 1
        context["prev_label"] = tax_year_label(start_year - 1)
        context["next_year"] = start_year + 1
        context["next_label"] = tax_year_label(start_year + 1)
        return context


class TaxSummaryCSVView(LoginRequiredMixin, View):
    def get(self, request):
        start_year = _requested_start_year(request)
        summary = build_tax_summary(start_year)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="tax-summary-{summary["label"].replace("/", "-")}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(
            [
                "Quarter",
                "PAYE income",
                "Self-employed income",
                "Self-employed expenses",
                "Self-employed net",
            ]
        )
        for row in summary["rows"]:
            writer.writerow(
                [
                    row["label"],
                    row["paye_income"],
                    row["self_employed_income"],
                    row["self_employed_expenses"],
                    row["self_employed_net"],
                ]
            )
        totals = summary["totals"]
        writer.writerow(
            [
                "Tax year total",
                totals["paye_income"],
                totals["self_employed_income"],
                totals["self_employed_expenses"],
                totals["self_employed_net"],
            ]
        )
        return response


class TaxSummaryPDFView(LoginRequiredMixin, View):
    def get(self, request):
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        start_year = _requested_start_year(request)
        summary = build_tax_summary(start_year)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="tax-summary-{summary["label"].replace("/", "-")}.pdf"'
        )

        doc = SimpleDocTemplate(response, pagesize=A4, title=f"Tax summary {summary['label']}")
        styles = getSampleStyleSheet()
        elements = [
            Paragraph(f"ShiftGuard tax summary — {summary['label']}", styles["Title"]),
            Spacer(1, 6 * mm),
        ]

        data = [
            [
                "Quarter",
                "PAYE income",
                "Self-employed income",
                "Self-employed expenses",
                "Self-employed net",
            ]
        ]
        for row in summary["rows"]:
            data.append(
                [
                    row["label"],
                    f"£{row['paye_income']}",
                    f"£{row['self_employed_income']}",
                    f"£{row['self_employed_expenses']}",
                    f"£{row['self_employed_net']}",
                ]
            )
        totals = summary["totals"]
        data.append(
            [
                "Tax year total",
                f"£{totals['paye_income']}",
                f"£{totals['self_employed_income']}",
                f"£{totals['self_employed_expenses']}",
                f"£{totals['self_employed_net']}",
            ]
        )

        table = Table(data, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e2e8f0")),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 6 * mm))
        elements.append(
            Paragraph(
                f"Year-to-date self-employed income: £{summary['ytd']['self_employed_income']} "
                f"&mdash; expenses: £{summary['ytd']['expenses_total']} "
                f"&mdash; net: £{summary['ytd']['self_employed_net']}",
                styles["Normal"],
            )
        )

        doc.build(elements)
        return response
