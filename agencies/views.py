from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import AgencyForm, SiteForm
from .models import Agency, Site


class AgencyListView(ListView):
    model = Agency
    template_name = "agencies/agency_list.html"
    context_object_name = "agencies"


class AgencyCreateView(CreateView):
    model = Agency
    form_class = AgencyForm
    template_name = "agencies/agency_form.html"
    success_url = reverse_lazy("agencies:agency-list")

    def form_valid(self, form):
        messages.success(self.request, f"Added agency {form.instance.name}.")
        return super().form_valid(form)


class AgencyUpdateView(UpdateView):
    model = Agency
    form_class = AgencyForm
    template_name = "agencies/agency_form.html"
    success_url = reverse_lazy("agencies:agency-list")


class AgencyDeleteView(DeleteView):
    model = Agency
    template_name = "agencies/agency_confirm_delete.html"
    success_url = reverse_lazy("agencies:agency-list")


class SiteListView(ListView):
    model = Site
    template_name = "agencies/site_list.html"
    context_object_name = "sites"

    def get_queryset(self):
        return Site.objects.select_related("agency").all()


class SiteCreateView(CreateView):
    model = Site
    form_class = SiteForm
    template_name = "agencies/site_form.html"
    success_url = reverse_lazy("agencies:site-list")

    def form_valid(self, form):
        messages.success(self.request, f"Added site {form.instance.name}.")
        return super().form_valid(form)


class SiteUpdateView(UpdateView):
    model = Site
    form_class = SiteForm
    template_name = "agencies/site_form.html"
    success_url = reverse_lazy("agencies:site-list")


class SiteDeleteView(DeleteView):
    model = Site
    template_name = "agencies/site_confirm_delete.html"
    success_url = reverse_lazy("agencies:site-list")
