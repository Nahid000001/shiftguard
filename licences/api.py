from rest_framework import viewsets

from .models import Licence
from .serializers import LicenceSerializer


class LicenceViewSet(viewsets.ModelViewSet):
    queryset = Licence.objects.all()
    serializer_class = LicenceSerializer
