from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ShiftForm
from .models import Shift


class ShiftListView(LoginRequiredMixin, ListView):
    model = Shift
    template_name = "shifts/shift_list.html"
    context_object_name = "shifts"
    paginate_by = 30

    def get_queryset(self):
        return Shift.objects.select_related("site", "site__agency").all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_shifts"] = Shift.objects.exists()
        return context


class ShiftCreateView(LoginRequiredMixin, CreateView):
    model = Shift
    form_class = ShiftForm
    template_name = "shifts/shift_form.html"
    success_url = reverse_lazy("shifts:list")

    def get_initial(self):
        initial = super().get_initial()
        if self.request.GET.get("duplicate"):
            last_shift = Shift.objects.select_related("site").first()
            if last_shift:
                initial.update(
                    {
                        "site": last_shift.site_id,
                        "date": date.today(),
                        "start_time": last_shift.start_time,
                        "end_time": last_shift.end_time,
                        "hourly_rate": last_shift.hourly_rate,
                        "shift_type": last_shift.shift_type,
                    }
                )
        return initial

    def form_valid(self, form):
        messages.success(self.request, "Shift logged.")
        return super().form_valid(form)


class ShiftUpdateView(LoginRequiredMixin, UpdateView):
    model = Shift
    form_class = ShiftForm
    template_name = "shifts/shift_form.html"
    success_url = reverse_lazy("shifts:list")


class ShiftDeleteView(LoginRequiredMixin, DeleteView):
    model = Shift
    template_name = "shifts/shift_confirm_delete.html"
    success_url = reverse_lazy("shifts:list")
