from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.services import (
    get_or_create_google_user,
    send_verification_email,
    start_email_verification,
)

User = get_user_model()


def public_post_view(view_func):
    """For a POST endpoint reachable before login (register/login/...).

    DRF's @api_view marks every view csrf_exempt at the Python level (a
    fresh wrapper object with that flag baked on), and SessionAuthentication
    only enforces CSRF for already-authenticated requests - neither applies
    pre-login, so without this the endpoint would accept a "login/register
    CSRF" (forcing a victim into an attacker-controlled account) from any
    origin. Un-exempt the object before wrapping it, so csrf_protect's check
    (which itself also honours csrf_exempt) actually runs.
    """
    view_func.csrf_exempt = False
    return csrf_protect(view_func)


@api_view(["GET"])
@permission_classes([AllowAny])
def csrf_view(request):
    """Forces Django to set the csrftoken cookie, so the frontend has a token
    to send back as X-CSRFToken on the login/register POST that follows."""
    get_token(request)
    return Response({"detail": "CSRF cookie set"})


@public_post_view
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username", "")
    password = request.data.get("password", "")
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({"detail": "Invalid username or password."}, status=400)
    login(request, user)
    return Response({"username": user.username})


@public_post_view
@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    username = (request.data.get("username") or "").strip()
    email = (request.data.get("email") or "").strip()
    password = request.data.get("password") or ""

    errors = {}
    if not username:
        errors["username"] = ["This field is required."]
    elif User.objects.filter(username__iexact=username).exists():
        errors["username"] = ["That username is already taken."]

    if not password:
        errors["password"] = ["This field is required."]
    else:
        try:
            # An unsaved instance lets UserAttributeSimilarityValidator check
            # the password against this username/email, same as at login time.
            validate_password(password, user=User(username=username, email=email))
        except DjangoValidationError as exc:
            errors["password"] = list(exc.messages)

    if errors:
        return Response(errors, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    if email:
        start_email_verification(user, email)
        send_verification_email(user, email, request)
    login(request, user)
    return Response({"username": user.username}, status=201)


@public_post_view
@api_view(["POST"])
@permission_classes([AllowAny])
def google_login_view(request):
    """Verifies a Google Identity Services ID token (the credential from the
    "Sign in with Google" button) and logs in the matching user, creating one
    on first sign-in. No client secret involved - this is ID-token
    verification, not the authorization-code OAuth flow."""
    if not settings.GOOGLE_CLIENT_ID:
        return Response(
            {"detail": "Google sign-in is not configured on this server."}, status=503
        )

    credential = request.data.get("credential")
    if not credential:
        return Response({"detail": "Missing credential."}, status=400)

    try:
        claims = google_id_token.verify_oauth2_token(
            credential, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except ValueError:
        return Response({"detail": "Invalid Google credential."}, status=400)

    email = claims.get("email")
    if not email or not claims.get("email_verified"):
        return Response({"detail": "Google account has no verified email."}, status=400)

    user = get_or_create_google_user(email)
    login(request, user)
    return Response({"username": user.username})


@api_view(["POST"])
def logout_view(request):
    logout(request)
    return Response({"detail": "Logged out."})


@api_view(["GET"])
def me_view(request):
    return Response({"username": request.user.username})
