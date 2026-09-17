from datetime import date, time
from decimal import Decimal

from django.test import TestCase

from agencies.models import Agency, Site
from expenses.models import Expense
from shifts.models import Shift

from .services import build_tax_summary
from .utils import tax_quarters, tax_year_label, tax_year_start_year


class TaxYearBoundaryTests(TestCase):
    def test_start_year_before_6_april_is_previous_tax_year(self):
        self.assertEqual(tax_year_start_year(date(2026, 4, 5)), 2025)

    def test_start_year_on_or_after_6_april_is_current_tax_year(self):
        self.assertEqual(tax_year_start_year(date(2026, 4, 6)), 2026)

    def test_label_formats_as_uk_tax_year(self):
        self.assertEqual(tax_year_label(2026), "2026/27")

    def test_quarters_cover_the_full_year_with_no_gaps(self):
        quarters = tax_quarters(2026)
        self.assertEqual(quarters[0]["start"], date(2026, 4, 6))
        self.assertEqual(quarters[-1]["end"], date(2027, 4, 5))
        for prev, nxt in zip(quarters, quarters[1:]):
            self.assertEqual(nxt["start"] - prev["end"], __import__("datetime").timedelta(days=1))


class TaxSummaryServiceTests(TestCase):
    def setUp(self):
        self.mitie = Agency.objects.create(name="Mitie", employment_type=Agency.EmploymentType.PAYE)
        self.r5 = Agency.objects.create(
            name="R5 Global", employment_type=Agency.EmploymentType.SELF_EMPLOYED
        )
        self.paye_site = Site.objects.create(agency=self.mitie, name="PAYE Site")
        self.se_site = Site.objects.create(agency=self.r5, name="SE Site")

    def _shift(self, site, on_date, rate=Decimal("10.00")):
        return Shift.objects.create(
            site=site, date=on_date, start_time=time(9, 0), end_time=time(17, 0), hourly_rate=rate
        )

    def test_shift_a_day_either_side_of_the_boundary_lands_in_different_tax_years(self):
        self._shift(self.paye_site, date(2026, 4, 5), rate=Decimal("10.00"))  # last day of 2025/26
        self._shift(self.paye_site, date(2026, 4, 6), rate=Decimal("20.00"))  # first day of 2026/27

        old_year = build_tax_summary(2025)
        new_year = build_tax_summary(2026)

        self.assertEqual(old_year["totals"]["paye_income"], Decimal("80.00"))
        self.assertEqual(new_year["totals"]["paye_income"], Decimal("160.00"))

    def test_income_splits_by_agency_employment_type(self):
        self._shift(self.paye_site, date(2026, 5, 1), rate=Decimal("10.00"))
        self._shift(self.se_site, date(2026, 5, 1), rate=Decimal("20.00"))

        summary = build_tax_summary(2026)

        self.assertEqual(summary["totals"]["paye_income"], Decimal("80.00"))
        self.assertEqual(summary["totals"]["self_employed_income"], Decimal("160.00"))

    def test_expense_tagged_to_paye_agency_does_not_reduce_self_employed_net(self):
        """Regression test: a PAYE-linked expense must not offset self-employment
        profit, since PAYE income carries no self-assessment expense deduction."""
        self._shift(self.se_site, date(2026, 5, 1), rate=Decimal("20.00"))  # £160 SE income
        Expense.objects.create(
            date=date(2026, 5, 1), category=Expense.Category.TRAVEL, amount=Decimal("50.00"),
            agency=self.mitie,
        )

        summary = build_tax_summary(2026)

        self.assertEqual(summary["totals"]["self_employed_expenses"], Decimal("0.00"))
        self.assertEqual(summary["totals"]["self_employed_net"], Decimal("160.00"))

    def test_expense_tagged_to_self_employed_agency_reduces_net(self):
        self._shift(self.se_site, date(2026, 5, 1), rate=Decimal("20.00"))  # £160 SE income
        Expense.objects.create(
            date=date(2026, 5, 1), category=Expense.Category.TRAVEL, amount=Decimal("25.00"),
            agency=self.r5,
        )

        summary = build_tax_summary(2026)

        self.assertEqual(summary["totals"]["self_employed_expenses"], Decimal("25.00"))
        self.assertEqual(summary["totals"]["self_employed_net"], Decimal("135.00"))

    def test_untagged_expense_counts_against_self_employed_net(self):
        self._shift(self.se_site, date(2026, 5, 1), rate=Decimal("20.00"))
        Expense.objects.create(
            date=date(2026, 5, 1), category=Expense.Category.OTHER, amount=Decimal("10.00"),
            agency=None,
        )

        summary = build_tax_summary(2026)

        self.assertEqual(summary["totals"]["self_employed_expenses"], Decimal("10.00"))

    def test_ytd_excludes_future_quarters(self):
        self._shift(self.se_site, date.today(), rate=Decimal("20.00"))
        start_year = tax_year_start_year()

        summary = build_tax_summary(start_year)

        self.assertEqual(summary["ytd"]["self_employed_income"], summary["totals"]["self_employed_income"])
