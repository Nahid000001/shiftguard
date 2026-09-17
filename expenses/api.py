from rest_framework import viewsets

from .models import Expense
from .serializers import ExpenseSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related("agency").all()
    serializer_class = ExpenseSerializer
    filterset_fields = {
        "date": ["exact", "gte", "lte"],
        "category": ["exact"],
        "agency": ["exact"],
    }
