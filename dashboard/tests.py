from datetime import date, time

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from agencies.models import Agency, Site
from shifts.models import Shift


class AuthGateTests(TestCase):
    """Every page in the app must require login - this is the whole point of
    Phase 3's auth work, so a regression here (e.g. a missing
    LoginRequiredMixin on a new view) should fail loudly."""

    protected_urls = [
        "dashboard:index",
        "dashboard:charts",
        "shifts:list",
        "agencies:agency-list",
        "agencies:site-list",
        "licences:list",
        "expenses:list",
        "reports:tax-summary",
    ]

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpass123")

    def test_anonymous_requests_redirect_to_login(self):
        for name in self.protected_urls:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, f"{name} did not redirect anonymous users")
            self.assertIn(reverse("login"), response.url)

    def test_authenticated_requests_succeed(self):
        self.client.force_login(self.user)
        for name in self.protected_urls:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, f"{name} failed for a logged-in user")

    def test_api_requires_authentication(self):
        response = self.client.get("/api/agencies/")
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.user)
        response = self.client.get("/api/agencies/")
        self.assertEqual(response.status_code, 200)


class DashboardAndChartsAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpass123")
        self.client.force_login(self.user)
        agency = Agency.objects.create(name="Mitie", employment_type=Agency.EmploymentType.PAYE)
        self.site = Site.objects.create(agency=agency, name="BNY Mellon")
        Shift.objects.create(
            site=self.site, date=date.today(), start_time=time(9, 0), end_time=time(17, 0),
            hourly_rate="10.00",
        )

    def test_api_endpoints_require_authentication(self):
        self.client.logout()
        for name in ["api-dashboard-summary", "api-dashboard-charts", "api-tax-summary"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 403, f"{name} did not require auth")

    def test_dashboard_summary_api_matches_the_template_view(self):
        api_response = self.client.get(reverse("api-dashboard-summary"))
        self.assertEqual(api_response.status_code, 200)
        self.assertEqual(api_response.json()["week_total"], 80.0)
        self.assertEqual(len(api_response.json()["week_shifts"]), 1)
        self.assertEqual(api_response.json()["week_shifts"][0]["site_name"], "BNY Mellon")

    def test_charts_api_reflects_real_data(self):
        response = self.client.get(reverse("api-dashboard-charts"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["has_data"])
        self.assertEqual(data["hours_by_agency"], [{"name": "Mitie", "value": 8.0, "color_index": 0}])

    def test_tax_summary_api_matches_the_csv_export(self):
        api_data = self.client.get(reverse("api-tax-summary")).json()
        csv_response = self.client.get(reverse("reports:tax-summary-csv"))
        self.assertEqual(api_data["totals"]["paye_income"], 80.0)
        self.assertIn(b"80.00", csv_response.content)
