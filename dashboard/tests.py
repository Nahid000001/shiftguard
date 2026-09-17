from datetime import date, time

from django.contrib.auth.models import User
from django.test import Client, TestCase
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


class AuthAPITests(TestCase):
    """Uses a CSRF-enforcing client (Django's test client skips CSRF checks by
    default) so these tests actually exercise the same protection a real
    browser-based frontend would hit, not a bypassed version of it."""

    client_class = Client

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpass123")
        self.client = Client(enforce_csrf_checks=True)

    def _csrf_token(self):
        self.client.get(reverse("api-auth-csrf"))
        return self.client.cookies["csrftoken"].value

    def test_csrf_endpoint_sets_cookie_without_requiring_login(self):
        response = self.client.get(reverse("api-auth-csrf"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)

    def test_login_without_csrf_token_is_rejected(self):
        response = self.client.post(
            reverse("api-auth-login"), {"username": "tester", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, 403)

    def test_login_with_correct_credentials_and_csrf_token_authenticates(self):
        token = self._csrf_token()
        response = self.client.post(
            reverse("api-auth-login"),
            {"username": "tester", "password": "testpass123"},
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "tester")

        me_response = self.client.get(reverse("api-auth-me"))
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.json()["username"], "tester")

    def test_login_with_wrong_password_is_rejected(self):
        token = self._csrf_token()
        response = self.client.post(
            reverse("api-auth-login"),
            {"username": "tester", "password": "wrongpassword"},
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 400)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("api-auth-me"))
        self.assertEqual(response.status_code, 403)

    def test_logout_ends_the_session(self):
        token = self._csrf_token()
        self.client.post(
            reverse("api-auth-login"),
            {"username": "tester", "password": "testpass123"},
            HTTP_X_CSRFTOKEN=token,
        )

        token = self._csrf_token()
        response = self.client.post(reverse("api-auth-logout"), HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)

        me_response = self.client.get(reverse("api-auth-me"))
        self.assertEqual(me_response.status_code, 403)
