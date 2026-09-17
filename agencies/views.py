from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import AgencyForm, SiteForm
from .models import Agency, Site


class AgencyListView(LoginRequiredMixin, ListView):
    template_name = "agencies/agency_list.html"
    context_object_name = "agencies"

    def get_queryset(self):
        return Agency.objects.filter(user=self.request.user)


class AgencyCreateView(LoginRequiredMixin, CreateView):
    model = Agency
    form_class = AgencyForm
    template_name = "agencies/agency_form.html"
    success_url = reverse_lazy("agencies:agency-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f"Added agency {form.instance.name}.")
        return super().form_valid(form)


class AgencyUpdateView(LoginRequiredMixin, UpdateView):
    form_class = AgencyForm
    template_name = "agencies/agency_form.html"
    success_url = reverse_lazy("agencies:agency-list")

    def get_queryset(self):
        return Agency.objects.filter(user=self.request.user)


class AgencyDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "agencies/agency_confirm_delete.html"
    success_url = reverse_lazy("agencies:agency-list")

    def get_queryset(self):
        return Agency.objects.filter(user=self.request.user)


class SiteListView(LoginRequiredMixin, ListView):
    template_name = "agencies/site_list.html"
    context_object_name = "sites"

    def get_queryset(self):
        return Site.objects.filter(agency__user=self.request.user).select_related("agency")


class SiteCreateView(LoginRequiredMixin, CreateView):
    model = Site
    form_class = SiteForm
    template_name = "agencies/site_form.html"
    success_url = reverse_lazy("agencies:site-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f"Added site {form.instance.name}.")
        return super().form_valid(form)


class SiteUpdateView(LoginRequiredMixin, UpdateView):
    form_class = SiteForm
    template_name = "agencies/site_form.html"
    success_url = reverse_lazy("agencies:site-list")

    def get_queryset(self):
        return Site.objects.filter(agency__user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class SiteDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "agencies/site_confirm_delete.html"
    success_url = reverse_lazy("agencies:site-list")

    def get_queryset(self):
        return Site.objects.filter(agency__user=self.request.user)
