from datetime import date, time
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from agencies.models import Agency, Site

from .models import Shift


class ShiftPayCalculationTests(TestCase):
    def setUp(self):
        agency = Agency.objects.create(name="Mitie", employment_type=Agency.EmploymentType.PAYE)
        self.site = Site.objects.create(agency=agency, name="Test Site")

    def test_standard_daytime_shift(self):
        shift = Shift.objects.create(
            site=self.site,
            date=date(2026, 1, 1),
            start_time=time(9, 0),
            end_time=time(17, 0),
            hourly_rate=Decimal("12.00"),
        )
        self.assertEqual(shift.duration_hours, 8)
        self.assertEqual(shift.calculated_pay, Decimal("96.00"))

    def test_overnight_shift_rolls_over_midnight(self):
        shift = Shift.objects.create(
            site=self.site,
            date=date(2026, 1, 1),
            start_time=time(22, 0),
            end_time=time(6, 0),
            hourly_rate=Decimal("15.00"),
        )
        self.assertEqual(shift.duration_hours, 8)
        self.assertEqual(shift.calculated_pay, Decimal("120.00"))

    def test_partial_hour_rounds_to_pence(self):
        shift = Shift.objects.create(
            site=self.site,
            date=date(2026, 1, 1),
            start_time=time(9, 0),
            end_time=time(12, 20),
            hourly_rate=Decimal("13.37"),
        )
        # 3h20m = 3.3333... hours
        self.assertEqual(shift.calculated_pay, Decimal("44.57"))


class DuplicateLastShiftTests(TestCase):
    def setUp(self):
        agency = Agency.objects.create(name="Mitie", employment_type=Agency.EmploymentType.PAYE)
        self.site = Site.objects.create(agency=agency, name="Test Site")
        self.user = User.objects.create_user(username="tester", password="testpass123")
        self.client.force_login(self.user)

    def test_prefills_from_most_recent_shift_with_todays_date(self):
        Shift.objects.create(
            site=self.site, date=date(2020, 1, 1), start_time=time(22, 0), end_time=time(6, 0),
            hourly_rate=Decimal("15.00"), shift_type=Shift.ShiftType.NIGHT,
        )

        response = self.client.get(reverse("shifts:create") + "?duplicate=1")

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.initial["site"], self.site.id)
        self.assertEqual(form.initial["date"], date.today())
        self.assertEqual(form.initial["hourly_rate"], Decimal("15.00"))
        self.assertEqual(form.initial["shift_type"], Shift.ShiftType.NIGHT)

    def test_no_prior_shifts_falls_back_to_blank_form(self):
        response = self.client.get(reverse("shifts:create") + "?duplicate=1")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("site", response.context["form"].initial)


class SiteDefaultRateAutofillTests(TestCase):
    """The shift form should embed each site's default_hourly_rate as a
    data-rate attribute so JS can auto-fill the rate field on site select."""

    def setUp(self):
        agency = Agency.objects.create(name="Mitie", employment_type=Agency.EmploymentType.PAYE)
        self.priced_site = Site.objects.create(
            agency=agency, name="Priced Site", default_hourly_rate=Decimal("14.98")
        )
        self.unpriced_site = Site.objects.create(agency=agency, name="Unpriced Site")
        self.user = User.objects.create_user(username="tester", password="testpass123")
        self.client.force_login(self.user)

    def test_site_with_default_rate_gets_data_rate_attribute(self):
        response = self.client.get(reverse("shifts:create"))
        self.assertContains(response, f'value="{self.priced_site.id}" data-rate="14.98"')

    def test_site_without_default_rate_has_no_data_rate_attribute(self):
        response = self.client.get(reverse("shifts:create"))
        self.assertNotContains(response, f'value="{self.unpriced_site.id}" data-rate')
