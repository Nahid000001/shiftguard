from datetime import date, time
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from agencies.models import Agency, Site

from .models import Shift


class ShiftPayCalculationTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="tester", password="testpass123")
        agency = Agency.objects.create(
            user=user, name="Mitie", employment_type=Agency.EmploymentType.PAYE
        )
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
        self.user = User.objects.create_user(username="tester", password="testpass123")
        agency = Agency.objects.create(
            user=self.user, name="Mitie", employment_type=Agency.EmploymentType.PAYE
        )
        self.site = Site.objects.create(agency=agency, name="Test Site")
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

    def test_duplicate_ignores_other_users_shifts(self):
        other = User.objects.create_user(username="other", password="testpass123")
        other_agency = Agency.objects.create(
            user=other, name="R5", employment_type=Agency.EmploymentType.SELF_EMPLOYED
        )
        other_site = Site.objects.create(agency=other_agency, name="Other Site")
        Shift.objects.create(
            site=other_site, date=date(2026, 6, 1), start_time=time(9, 0), end_time=time(17, 0),
            hourly_rate=Decimal("99.00"),
        )

        response = self.client.get(reverse("shifts:create") + "?duplicate=1")
        self.assertNotIn("site", response.context["form"].initial)


class SiteDefaultRateAutofillTests(TestCase):
    """The shift form should embed each site's default_hourly_rate as a
    data-rate attribute so JS can auto-fill the rate field on site select."""

    def setUp(self):
        user = User.objects.create_user(username="tester", password="testpass123")
        agency = Agency.objects.create(
            user=user, name="Mitie", employment_type=Agency.EmploymentType.PAYE
        )
        self.priced_site = Site.objects.create(
            agency=agency, name="Priced Site", default_hourly_rate=Decimal("14.98")
        )
        self.unpriced_site = Site.objects.create(agency=agency, name="Unpriced Site")
        self.client.force_login(user)

    def test_site_with_default_rate_gets_data_rate_attribute(self):
        response = self.client.get(reverse("shifts:create"))
        self.assertContains(response, f'value="{self.priced_site.id}" data-rate="14.98"')

    def test_site_without_default_rate_has_no_data_rate_attribute(self):
        response = self.client.get(reverse("shifts:create"))
        self.assertNotContains(response, f'value="{self.unpriced_site.id}" data-rate')


class ShiftAPIFilteringTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="tester", password="testpass123")
        agency = Agency.objects.create(
            user=user, name="Mitie", employment_type=Agency.EmploymentType.PAYE
        )
        self.site = Site.objects.create(agency=agency, name="Test Site")
        for d in [date(2026, 1, 5), date(2026, 2, 10), date(2026, 3, 15)]:
            Shift.objects.create(
                site=self.site, date=d, start_time=time(9, 0), end_time=time(17, 0),
                hourly_rate=Decimal("10.00"),
            )
        self.client.force_login(user)

    def test_list_is_paginated(self):
        response = self.client.get("/api/shifts/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(data["count"], 3)

    def test_date_range_filter_narrows_results(self):
        response = self.client.get("/api/shifts/?date__gte=2026-02-01&date__lte=2026-02-28")
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["date"], "2026-02-10")


class ShiftMultiUserIsolationTests(TestCase):
    """The whole point of multi-user support: one account must never see,
    edit, or delete another account's data - via the API or the template
    views, and never by attaching to another user's site/agency either."""

    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="testpass123")
        self.bob = User.objects.create_user(username="bob", password="testpass123")

        alice_agency = Agency.objects.create(
            user=self.alice, name="Mitie", employment_type=Agency.EmploymentType.PAYE
        )
        self.alice_site = Site.objects.create(agency=alice_agency, name="Alice Site")
        self.alice_shift = Shift.objects.create(
            site=self.alice_site, date=date(2026, 1, 1), start_time=time(9, 0), end_time=time(17, 0),
            hourly_rate=Decimal("10.00"),
        )

        bob_agency = Agency.objects.create(
            user=self.bob, name="Securitas", employment_type=Agency.EmploymentType.PAYE
        )
        self.bob_site = Site.objects.create(agency=bob_agency, name="Bob Site")
        self.bob_shift = Shift.objects.create(
            site=self.bob_site, date=date(2026, 1, 2), start_time=time(9, 0), end_time=time(17, 0),
            hourly_rate=Decimal("20.00"),
        )

    def test_api_list_only_shows_own_shifts(self):
        self.client.force_login(self.alice)
        response = self.client.get("/api/shifts/")
        ids = [row["id"] for row in response.json()["results"]]
        self.assertEqual(ids, [self.alice_shift.id])

    def test_api_cannot_fetch_another_users_shift_by_id(self):
        self.client.force_login(self.alice)
        response = self.client.get(f"/api/shifts/{self.bob_shift.id}/")
        self.assertEqual(response.status_code, 404)

    def test_api_cannot_attach_a_shift_to_another_users_site(self):
        self.client.force_login(self.alice)
        response = self.client.post(
            "/api/shifts/",
            {
                "site": self.bob_site.id,
                "date": "2026-01-03",
                "start_time": "09:00",
                "end_time": "17:00",
                "hourly_rate": "10.00",
                "shift_type": "STANDARD",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_template_list_only_shows_own_shifts(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse("shifts:list"))
        self.assertContains(response, "Alice Site")
        self.assertNotContains(response, "Bob Site")

    def test_template_cannot_edit_another_users_shift(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse("shifts:update", args=[self.bob_shift.id]))
        self.assertEqual(response.status_code, 404)

    def test_template_cannot_delete_another_users_shift(self):
        self.client.force_login(self.alice)
        response = self.client.post(reverse("shifts:delete", args=[self.bob_shift.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Shift.objects.filter(id=self.bob_shift.id).exists())
