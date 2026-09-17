from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .services import build_charts_data, build_dashboard_summary


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_dashboard_summary(self.request.user))
        return context


class ChartsView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/charts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_charts_data(self.request.user))
        return context
