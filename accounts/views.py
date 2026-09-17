from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View

from .models import email_verification_token
from .services import mark_email_verified

User = get_user_model()


class VerifyEmailView(View):
    template_name = "accounts/verify_email_result.html"

    def get(self, request, uidb64, token):
        user = None
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and email_verification_token.check_token(user, token):
            mark_email_verified(user)
            return render(self.request, self.template_name, {"success": True})

        return render(self.request, self.template_name, {"success": False})
