from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import EmailVerification, email_verification_token
from .services import (
    get_or_create_google_user,
    mark_email_verified,
    send_verification_email,
    start_email_verification,
)


class EmailVerificationTokenTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", email="alice@example.com")
        start_email_verification(self.user, "alice@example.com")

    def _link(self, user):
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        return reverse("verify-email", kwargs={"uidb64": uidb64, "token": token})

    def test_valid_link_marks_the_email_verified(self):
        response = self.client.get(self._link(self.user))
        self.assertEqual(response.status_code, 200)
        self.user.email_verification.refresh_from_db()
        self.assertTrue(self.user.email_verification.verified)
        self.assertIsNotNone(self.user.email_verification.verified_at)

    def test_link_is_single_use(self):
        link = self._link(self.user)
        self.client.get(link)
        # The token's hash includes the verified flag, so it flips to
        # invalid the moment it's used once - a captured/forwarded link
        # can't be replayed to "re-verify" (a no-op) or confuse state.
        second_response = self.client.get(link)
        self.assertContains(second_response, "invalid or expired")

    def test_tampered_token_is_rejected(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        response = self.client.get(
            reverse("verify-email", kwargs={"uidb64": uidb64, "token": "garbage-token"})
        )
        self.assertContains(response, "invalid or expired")
        self.assertFalse(self.user.email_verification.verified)

    def test_nonexistent_user_id_is_rejected_not_500(self):
        uidb64 = urlsafe_base64_encode(force_bytes(999999))
        response = self.client.get(
            reverse("verify-email", kwargs={"uidb64": uidb64, "token": "whatever"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "invalid or expired")

    def test_registering_sends_a_verification_email(self):
        mail.outbox.clear()
        request = RequestFactory().get("/")
        send_verification_email(self.user, "alice@example.com", request)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("alice@example.com", mail.outbox[0].to)
        self.assertIn("verify-email", mail.outbox[0].body)


@override_settings(GOOGLE_CLIENT_ID="fake-client-id.apps.googleusercontent.com")
class GoogleSignInEmailTrustTests(TestCase):
    """The actual vulnerability this fix closes: someone registers with a
    victim's email (never proving they own it), then the real victim signs
    in with Google using that same, genuinely-verified-by-Google email.
    Before the fix, that logged the victim straight into the squatter's
    pre-made account. It must not."""

    def test_unverified_existing_email_does_not_get_linked(self):
        squatter = User.objects.create_user(username="squatter", email="victim@example.com")
        start_email_verification(squatter, "victim@example.com")

        real_owner = get_or_create_google_user("victim@example.com")

        self.assertNotEqual(real_owner.pk, squatter.pk)
        self.assertEqual(User.objects.filter(email="victim@example.com").count(), 2)

    def test_verified_existing_email_does_get_linked(self):
        user = User.objects.create_user(username="alice", email="alice@example.com")
        record = start_email_verification(user, "alice@example.com")
        mark_email_verified(user)
        record.refresh_from_db()

        result = get_or_create_google_user("alice@example.com")

        self.assertEqual(result.pk, user.pk)

    def test_brand_new_email_creates_a_verified_account(self):
        user = get_or_create_google_user("newperson@example.com")
        self.assertEqual(user.email, "newperson@example.com")
        self.assertTrue(user.email_verification.verified)
        self.assertFalse(user.has_usable_password())

    def _csrf_token(self, client):
        client.get(reverse("api-auth-csrf"))
        return client.cookies["csrftoken"].value

    @patch("shiftguard.auth_api.google_id_token.verify_oauth2_token")
    def test_api_view_never_logs_a_google_sign_in_into_an_unverified_squatted_account(
        self, mock_verify
    ):
        """Drives the real /api/auth/google/ endpoint end-to-end (mocking
        only the Google-side JWT verification, which needs Google's live
        infrastructure) - catches a regression where someone reverts the
        view back to a blind email match, not just tests the helper in
        isolation."""
        squatter = User.objects.create_user(username="squatter", email="victim@example.com")
        start_email_verification(squatter, "victim@example.com")
        mock_verify.return_value = {"email": "victim@example.com", "email_verified": True}

        client = Client(enforce_csrf_checks=True)
        token = self._csrf_token(client)
        response = client.post(
            reverse("api-auth-google"), {"credential": "fake-but-mocked"}, HTTP_X_CSRFTOKEN=token
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.json()["username"], "squatter")
