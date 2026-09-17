from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Licence


class LicenceExpiryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpass123")

    def _licence(self, expiry_offset_days, reminder_days_before=60):
        today = date.today()
        return Licence.objects.create(
            user=self.user,
            name="SIA Door Supervisor",
            licence_number="123456789",
            issue_date=today - timedelta(days=1000),
            expiry_date=today + timedelta(days=expiry_offset_days),
            reminder_days_before=reminder_days_before,
        )

    def test_far_future_expiry_is_valid_not_expiring(self):
        licence = self._licence(400)
        self.assertFalse(licence.is_expired)
        self.assertFalse(licence.is_expiring_soon)

    def test_within_reminder_window_is_expiring_soon(self):
        licence = self._licence(20)
        self.assertFalse(licence.is_expired)
        self.assertTrue(licence.is_expiring_soon)

    def test_expiry_today_is_expiring_soon_not_expired(self):
        licence = self._licence(0)
        self.assertFalse(licence.is_expired)
        self.assertTrue(licence.is_expiring_soon)

    def test_past_expiry_is_expired(self):
        licence = self._licence(-5)
        self.assertTrue(licence.is_expired)
        self.assertEqual(licence.days_until_expiry, -5)

    def test_reminder_window_is_configurable(self):
        licence = self._licence(45, reminder_days_before=30)
        self.assertFalse(licence.is_expiring_soon)


class LicenceMultiUserIsolationTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="testpass123")
        self.bob = User.objects.create_user(username="bob", password="testpass123")
        today = date.today()
        self.alice_licence = Licence.objects.create(
            user=self.alice, name="Alice SIA licence", licence_number="111",
            issue_date=today, expiry_date=today + timedelta(days=365),
        )
        self.bob_licence = Licence.objects.create(
            user=self.bob, name="Bob SIA licence", licence_number="222",
            issue_date=today, expiry_date=today + timedelta(days=365),
        )

    def test_list_only_shows_own_licences(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse("licences:list"))
        self.assertContains(response, "Alice SIA licence")
        self.assertNotContains(response, "Bob SIA licence")

    def test_cannot_edit_another_users_licence(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse("licences:update", args=[self.bob_licence.id]))
        self.assertEqual(response.status_code, 404)

    def test_api_list_only_shows_own_licences(self):
        self.client.force_login(self.alice)
        response = self.client.get("/api/licences/")
        ids = [row["id"] for row in response.json()["results"]]
        self.assertEqual(ids, [self.alice_licence.id])
