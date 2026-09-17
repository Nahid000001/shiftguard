from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from agencies.models import Agency

from .models import Expense


class ExpenseCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpass123")
        self.client.force_login(self.user)

    def test_create_update_delete_round_trip(self):
        create_resp = self.client.post(
            reverse("expenses:create"),
            {"date": "2026-01-01", "category": "EQUIPMENT", "amount": "59.99", "agency": "", "notes": "Torch"},
        )
        self.assertEqual(create_resp.status_code, 302)
        expense = Expense.objects.get(notes="Torch")
        self.assertEqual(expense.amount, Decimal("59.99"))

        update_resp = self.client.post(
            reverse("expenses:update", args=[expense.pk]),
            {"date": "2026-01-01", "category": "EQUIPMENT", "amount": "75.00", "agency": "", "notes": "Torch"},
        )
        self.assertEqual(update_resp.status_code, 302)
        expense.refresh_from_db()
        self.assertEqual(expense.amount, Decimal("75.00"))

        delete_resp = self.client.post(reverse("expenses:delete", args=[expense.pk]))
        self.assertEqual(delete_resp.status_code, 302)
        self.assertFalse(Expense.objects.filter(pk=expense.pk).exists())

    def test_expense_can_be_linked_to_an_agency(self):
        agency = Agency.objects.create(name="Mitie", employment_type=Agency.EmploymentType.PAYE)
        expense = Expense.objects.create(date=date(2026, 1, 1), category="TRAVEL", amount=Decimal("10.00"), agency=agency)
        self.assertEqual(expense.agency, agency)
