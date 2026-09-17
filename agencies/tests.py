from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Agency, Site


class AgencyMultiUserIsolationTests(TestCase):
    """Multi-user is the whole point of registration existing at all - these
    lock in that one account can never see, edit, or delete another's
    agencies/sites, via the template views or the API."""

    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="testpass123")
        self.bob = User.objects.create_user(username="bob", password="testpass123")
        self.alice_agency = Agency.objects.create(
            user=self.alice, name="Alice Agency", employment_type=Agency.EmploymentType.PAYE
        )
        self.bob_agency = Agency.objects.create(
            user=self.bob, name="Bob Agency", employment_type=Agency.EmploymentType.PAYE
        )
        self.bob_site = Site.objects.create(agency=self.bob_agency, name="Bob Site")

    def test_agency_list_only_shows_own_agencies(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse("agencies:agency-list"))
        self.assertContains(response, "Alice Agency")
        self.assertNotContains(response, "Bob Agency")

    def test_cannot_edit_another_users_agency(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse("agencies:agency-update", args=[self.bob_agency.id]))
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_another_users_agency(self):
        self.client.force_login(self.alice)
        response = self.client.post(reverse("agencies:agency-delete", args=[self.bob_agency.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Agency.objects.filter(id=self.bob_agency.id).exists())

    def test_site_form_only_offers_own_agencies(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse("agencies:site-create"))
        self.assertNotContains(response, "Bob Agency")

    def test_cannot_attach_a_site_to_another_users_agency(self):
        self.client.force_login(self.alice)
        response = self.client.post(
            reverse("agencies:site-create"),
            {"agency": self.bob_agency.id, "name": "Sneaky Site", "address": "", "default_hourly_rate": ""},
        )
        self.assertEqual(response.status_code, 200)  # invalid choice, form re-rendered
        self.assertFalse(Site.objects.filter(name="Sneaky Site").exists())

    def test_api_agency_list_only_shows_own_agencies(self):
        self.client.force_login(self.alice)
        response = self.client.get("/api/agencies/")
        names = [row["name"] for row in response.json()["results"]]
        self.assertEqual(names, ["Alice Agency"])

    def test_api_cannot_attach_a_site_to_another_users_agency(self):
        self.client.force_login(self.alice)
        response = self.client.post(
            "/api/sites/", {"agency": self.bob_agency.id, "name": "Sneaky Site"}
        )
        self.assertEqual(response.status_code, 400)

    def test_api_created_agency_is_owned_by_the_creator(self):
        self.client.force_login(self.alice)
        response = self.client.post(
            "/api/agencies/", {"name": "New Agency", "employment_type": "PAYE", "contact_notes": ""}
        )
        self.assertEqual(response.status_code, 201)
        created = Agency.objects.get(name="New Agency")
        self.assertEqual(created.user, self.alice)
