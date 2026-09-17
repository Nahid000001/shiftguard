from datetime import date, timedelta

from django.test import TestCase

from .models import Licence


class LicenceExpiryTests(TestCase):
    def _licence(self, expiry_offset_days, reminder_days_before=60):
        today = date.today()
        return Licence.objects.create(
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
