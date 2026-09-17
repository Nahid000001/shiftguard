from rest_framework import viewsets

from .models import Agency, Site
from .serializers import AgencySerializer, SiteSerializer


class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.select_related("agency").all()
    serializer_class = SiteSerializer
