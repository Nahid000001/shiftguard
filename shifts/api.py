from rest_framework import viewsets

from .models import Shift
from .serializers import ShiftSerializer


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.select_related("site", "site__agency").all()
    serializer_class = ShiftSerializer
    filterset_fields = {
        "date": ["exact", "gte", "lte"],
        "site": ["exact"],
        "site__agency": ["exact"],
        "shift_type": ["exact"],
    }
