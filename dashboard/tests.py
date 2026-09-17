from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


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
