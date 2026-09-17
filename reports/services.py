from datetime import date
from decimal import Decimal

from agencies.models import Agency
from expenses.models import Expense
from shifts.models import Shift

from .utils import tax_quarters, tax_year_label


def _sum_pay(shifts):
    return sum((s.calculated_pay for s in shifts), Decimal("0.00"))


def build_tax_summary(start_year):
    """Build the PAYE vs self-employed income/expense breakdown for a UK tax year."""
    quarters = tax_quarters(start_year)
    today = date.today()

    shifts = list(
        Shift.objects.filter(date__gte=quarters[0]["start"], date__lte=quarters[-1]["end"])
        .select_related("site", "site__agency")
    )
    expenses = list(
        Expense.objects.filter(date__gte=quarters[0]["start"], date__lte=quarters[-1]["end"])
    )

    rows = []
    for q in quarters:
        q_shifts = [s for s in shifts if q["start"] <= s.date <= q["end"]]
        q_expenses = [e for e in expenses if q["start"] <= e.date <= q["end"]]

        paye_income = _sum_pay(
            s for s in q_shifts if s.site.agency.employment_type == Agency.EmploymentType.PAYE
        )
        self_employed_income = _sum_pay(
            s
            for s in q_shifts
            if s.site.agency.employment_type == Agency.EmploymentType.SELF_EMPLOYED
        )
        # Only expenses with no agency, or one tagged self-employed, count against
        # self-employed net profit — an expense linked to a PAYE agency isn't a
        # self-assessment deduction and must not reduce this figure.
        self_employed_expenses = sum(
            (
                e.amount
                for e in q_expenses
                if e.agency is None or e.agency.employment_type == Agency.EmploymentType.SELF_EMPLOYED
            ),
            Decimal("0.00"),
        )
        expenses_total = sum((e.amount for e in q_expenses), Decimal("0.00"))

        rows.append(
            {
                "label": q["label"],
                "start": q["start"],
                "end": q["end"],
                "is_future": q["start"] > today,
                "paye_income": paye_income,
                "self_employed_income": self_employed_income,
                "expenses_total": expenses_total,
                "self_employed_expenses": self_employed_expenses,
                "self_employed_net": self_employed_income - self_employed_expenses,
            }
        )

    ytd_rows = [r for r in rows if not r["is_future"]]
    totals = {
        "paye_income": sum((r["paye_income"] for r in rows), Decimal("0.00")),
        "self_employed_income": sum((r["self_employed_income"] for r in rows), Decimal("0.00")),
        "expenses_total": sum((r["expenses_total"] for r in rows), Decimal("0.00")),
        "self_employed_expenses": sum(
            (r["self_employed_expenses"] for r in rows), Decimal("0.00")
        ),
        "self_employed_net": sum((r["self_employed_net"] for r in rows), Decimal("0.00")),
    }
    ytd = {
        "self_employed_income": sum(
            (r["self_employed_income"] for r in ytd_rows), Decimal("0.00")
        ),
        "expenses_total": sum(
            (r["self_employed_expenses"] for r in ytd_rows), Decimal("0.00")
        ),
    }
    ytd["self_employed_net"] = ytd["self_employed_income"] - ytd["expenses_total"]

    return {
        "start_year": start_year,
        "label": tax_year_label(start_year),
        "rows": rows,
        "totals": totals,
        "ytd": ytd,
    }
