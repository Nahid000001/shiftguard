from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import models


class EmailVerification(models.Model):
    """Tracks whether a user has proven ownership of the email on their
    account - the one thing standing between "Sign in with Google" and
    silently logging someone into an account a different person registered
    by typing in the victim's email address (see EmailVerificationTokenGenerator
    and get_or_create_google_user in services.py for how this is enforced)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_verification"
    )
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} ({'verified' if self.verified else 'unverified'})"


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """A verification link becomes invalid once used, because the hash
    includes the verified flag - the same trick Django's own password-reset
    tokens use with last_login, just keyed on a different piece of state."""

    def _make_hash_value(self, user, timestamp):
        record = getattr(user, "email_verification", None)
        verified = record.verified if record else False
        email = record.email if record else user.email
        return f"{user.pk}{email}{verified}{timestamp}"


email_verification_token = EmailVerificationTokenGenerator()
