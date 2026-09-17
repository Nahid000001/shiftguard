from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import LicenceForm
from .models import Licence


class LicenceListView(LoginRequiredMixin, ListView):
    template_name = "licences/licence_list.html"
    context_object_name = "licences"

    def get_queryset(self):
        return Licence.objects.filter(user=self.request.user)


class LicenceCreateView(LoginRequiredMixin, CreateView):
    model = Licence
    form_class = LicenceForm
    template_name = "licences/licence_form.html"
    success_url = reverse_lazy("licences:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f"Added licence {form.instance.name}.")
        return super().form_valid(form)


class LicenceUpdateView(LoginRequiredMixin, UpdateView):
    form_class = LicenceForm
    template_name = "licences/licence_form.html"
    success_url = reverse_lazy("licences:list")

    def get_queryset(self):
        return Licence.objects.filter(user=self.request.user)


class LicenceDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "licences/licence_confirm_delete.html"
    success_url = reverse_lazy("licences:list")

    def get_queryset(self):
        return Licence.objects.filter(user=self.request.user)
