from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import EmailVerification, email_verification_token

User = get_user_model()


def start_email_verification(user, email):
    """Called right after a manual registration that gave an email address.
    Creates the unverified record - Google sign-in won't trust this email
    for this account until the link below is clicked."""
    if not email:
        return None
    return EmailVerification.objects.create(user=user, email=email, verified=False)


def send_verification_email(user, email, request):
    record = getattr(user, "email_verification", None)
    if record is None or record.email != email:
        return
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    path = reverse("verify-email", kwargs={"uidb64": uidb64, "token": token})
    link = request.build_absolute_uri(path)
    send_mail(
        subject="Verify your ShiftGuard email",
        message=(
            f"Confirm this is your email address:\n\n{link}\n\n"
            "Until you do, \"Sign in with Google\" won't be able to use this "
            "address to log into this account - it'll only ever create a "
            "separate one, so nobody can pre-register your email to "
            "intercept your Google sign-in."
        ),
        from_email=None,  # uses DEFAULT_FROM_EMAIL
        recipient_list=[email],
        fail_silently=True,
    )


def mark_email_verified(user):
    record = getattr(user, "email_verification", None)
    if record is None:
        return False
    record.verified = True
    record.verified_at = timezone.now()
    record.save(update_fields=["verified", "verified_at"])
    return True


def _unique_username(base):
    username = base
    suffix = 1
    while User.objects.filter(username=username).exists():
        suffix += 1
        username = f"{base}-{suffix}"
    return username


def get_or_create_google_user(email):
    """The core of the email-verification fix: only log a Google sign-in
    into an *existing* account if that account's claim to this email was
    actually verified. An unverified account with a matching email (e.g. one
    someone else registered by typing in this email, never proving they own
    it) is never trusted - a fresh account is created instead, so the real
    owner of the Google account always lands somewhere safe and never
    inherits a stranger's pre-made account."""
    verified_match = User.objects.filter(
        email=email, email_verification__verified=True
    ).first()
    if verified_match is not None:
        return verified_match

    username = _unique_username(email)
    user = User.objects.create_user(username=username, email=email)
    user.set_unusable_password()
    user.save()
    EmailVerification.objects.create(
        user=user, email=email, verified=True, verified_at=timezone.now()
    )
    return user
