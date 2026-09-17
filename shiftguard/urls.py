from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from agencies.api import AgencyViewSet, SiteViewSet
from dashboard.api import charts_data_api, dashboard_summary_api
from shiftguard.auth_api import csrf_view, login_view, logout_view, me_view
from expenses.api import ExpenseViewSet
from licences.api import LicenceViewSet
from reports.api import tax_summary_api
from shifts.api import ShiftViewSet

router = DefaultRouter()
router.register("agencies", AgencyViewSet)
router.register("sites", SiteViewSet)
router.register("shifts", ShiftViewSet)
router.register("licences", LicenceViewSet)
router.register("expenses", ExpenseViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/', include(router.urls)),
    path('api/dashboard/summary/', dashboard_summary_api, name='api-dashboard-summary'),
    path('api/dashboard/charts/', charts_data_api, name='api-dashboard-charts'),
    path('api/reports/tax-summary/', tax_summary_api, name='api-tax-summary'),
    path('api/auth/csrf/', csrf_view, name='api-auth-csrf'),
    path('api/auth/login/', login_view, name='api-auth-login'),
    path('api/auth/logout/', logout_view, name='api-auth-logout'),
    path('api/auth/me/', me_view, name='api-auth-me'),
    path('', include('dashboard.urls')),
    path('agencies/', include('agencies.urls')),
    path('shifts/', include('shifts.urls')),
    path('licences/', include('licences.urls')),
    path('expenses/', include('expenses.urls')),
    path('reports/', include('reports.urls')),
]
