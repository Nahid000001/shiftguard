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
        agency = Agency.objects.create(
            user=self.user, name="Mitie", employment_type=Agency.EmploymentType.PAYE
        )
        expense = Expense.objects.create(
            user=self.user, date=date(2026, 1, 1), category="TRAVEL", amount=Decimal("10.00"), agency=agency
        )
        self.assertEqual(expense.agency, agency)


class ExpenseMultiUserIsolationTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="testpass123")
        self.bob = User.objects.create_user(username="bob", password="testpass123")
        self.bob_agency = Agency.objects.create(
            user=self.bob, name="Bob's Agency", employment_type=Agency.EmploymentType.PAYE
        )
        self.alice_expense = Expense.objects.create(
            user=self.alice, date=date(2026, 1, 1), category="TRAVEL", amount=Decimal("10.00")
        )
        self.bob_expense = Expense.objects.create(
            user=self.bob, date=date(2026, 1, 1), category="TRAVEL", amount=Decimal("20.00")
        )

    def test_list_only_shows_own_expenses(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse("expenses:list"))
        self.assertContains(response, "£10.00")
        self.assertNotContains(response, "£20.00")

    def test_cannot_link_expense_to_another_users_agency(self):
        self.client.force_login(self.alice)
        response = self.client.post(
            reverse("expenses:create"),
            {
                "date": "2026-01-01", "category": "TRAVEL", "amount": "5.00",
                "agency": self.bob_agency.id, "notes": "",
            },
        )
        # Not in the scoped form's queryset, so it's a plain invalid-choice
        # validation error (re-rendered form), not a save.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expense.objects.filter(amount=Decimal("5.00")).count(), 0)

    def test_api_list_only_shows_own_expenses(self):
        self.client.force_login(self.alice)
        response = self.client.get("/api/expenses/")
        ids = [row["id"] for row in response.json()["results"]]
        self.assertEqual(ids, [self.alice_expense.id])
