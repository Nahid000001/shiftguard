from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ExpenseForm
from .models import Expense


class ExpenseListView(ListView):
    model = Expense
    template_name = "expenses/expense_list.html"
    context_object_name = "expenses"

    def get_queryset(self):
        return Expense.objects.select_related("agency").all()


class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "expenses/expense_form.html"
    success_url = reverse_lazy("expenses:list")

    def form_valid(self, form):
        messages.success(self.request, "Expense logged.")
        return super().form_valid(form)


class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "expenses/expense_form.html"
    success_url = reverse_lazy("expenses:list")


class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = "expenses/expense_confirm_delete.html"
    success_url = reverse_lazy("expenses:list")
