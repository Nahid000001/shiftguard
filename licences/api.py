from rest_framework import viewsets

from .models import Licence
from .serializers import LicenceSerializer


class LicenceViewSet(viewsets.ModelViewSet):
    serializer_class = LicenceSerializer

    def get_queryset(self):
        return Licence.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
