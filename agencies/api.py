from rest_framework import viewsets

from .models import Agency, Site
from .serializers import AgencySerializer, SiteSerializer


class AgencyViewSet(viewsets.ModelViewSet):
    serializer_class = AgencySerializer

    def get_queryset(self):
        return Agency.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SiteViewSet(viewsets.ModelViewSet):
    serializer_class = SiteSerializer

    def get_queryset(self):
        return Site.objects.filter(agency__user=self.request.user).select_related("agency")
