from rest_framework import viewsets

from .models import Shift
from .serializers import ShiftSerializer


class ShiftViewSet(viewsets.ModelViewSet):
    serializer_class = ShiftSerializer
    filterset_fields = {
        "date": ["exact", "gte", "lte"],
        "site": ["exact"],
        "site__agency": ["exact"],
        "shift_type": ["exact"],
    }

    def get_queryset(self):
        return Shift.objects.filter(site__agency__user=self.request.user).select_related(
            "site", "site__agency"
        )
