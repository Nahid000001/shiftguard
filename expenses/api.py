from rest_framework import viewsets

from .models import Expense
from .serializers import ExpenseSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    filterset_fields = {
        "date": ["exact", "gte", "lte"],
        "category": ["exact"],
        "agency": ["exact"],
    }

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user).select_related("agency")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
