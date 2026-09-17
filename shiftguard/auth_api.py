from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def csrf_view(request):
    """Forces Django to set the csrftoken cookie, so the frontend has a token
    to send back as X-CSRFToken on the login POST that follows."""
    get_token(request)
    return Response({"detail": "CSRF cookie set"})


@api_view(["POST"])
@permission_classes([AllowAny])
def _login_view(request):
    username = request.data.get("username", "")
    password = request.data.get("password", "")
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({"detail": "Invalid username or password."}, status=400)
    login(request, user)
    return Response({"username": user.username})


# DRF's @api_view marks every view csrf_exempt at the Python level (a fresh
# wrapper object with that flag baked on), and SessionAuthentication only
# enforces CSRF for already-authenticated requests - neither applies here
# (no session exists yet), so without this override the login endpoint would
# accept a "login CSRF" (forcing a victim to log into an attacker's account)
# from any origin. Un-exempt the object before wrapping it, so csrf_protect's
# check (which itself also honours csrf_exempt) actually runs.
_login_view.csrf_exempt = False
login_view = csrf_protect(_login_view)


@api_view(["POST"])
def logout_view(request):
    logout(request)
    return Response({"detail": "Logged out."})


@api_view(["GET"])
def me_view(request):
    return Response({"username": request.user.username})
