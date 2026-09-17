from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from agencies.api import AgencyViewSet, SiteViewSet
from expenses.api import ExpenseViewSet
from licences.api import LicenceViewSet
from shifts.api import ShiftViewSet

router = DefaultRouter()
router.register("agencies", AgencyViewSet)
router.register("sites", SiteViewSet)
router.register("shifts", ShiftViewSet)
router.register("licences", LicenceViewSet)
router.register("expenses", ExpenseViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('dashboard.urls')),
    path('agencies/', include('agencies.urls')),
    path('shifts/', include('shifts.urls')),
    path('licences/', include('licences.urls')),
    path('expenses/', include('expenses.urls')),
    path('reports/', include('reports.urls')),
]
