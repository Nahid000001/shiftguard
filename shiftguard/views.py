from django import forms
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.services import send_verification_email, start_email_verification


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta(UserCreationForm.Meta):
        fields = ("username", "email")


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        email = form.cleaned_data.get("email")
        if email:
            start_email_verification(self.object, email)
            send_verification_email(self.object, email, self.request)
        login(self.request, self.object)
        return response
