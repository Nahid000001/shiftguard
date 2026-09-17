from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from agencies.api import AgencyViewSet, SiteViewSet
from dashboard.api import charts_data_api, dashboard_summary_api
from shiftguard.auth_api import (
    csrf_view,
    google_login_view,
    login_view,
    logout_view,
    me_view,
    register_view,
)
from shiftguard.views import RegisterView
from accounts.views import VerifyEmailView
from expenses.api import ExpenseViewSet
from licences.api import LicenceViewSet
from reports.api import tax_summary_api
from shifts.api import ShiftViewSet

router = DefaultRouter()
router.register("agencies", AgencyViewSet, basename="agency")
router.register("sites", SiteViewSet, basename="site")
router.register("shifts", ShiftViewSet, basename="shift")
router.register("licences", LicenceViewSet, basename="licence")
router.register("expenses", ExpenseViewSet, basename="expense")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path(
        'accounts/password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.txt',
            subject_template_name='registration/password_reset_subject.txt',
        ),
        name='password_reset',
    ),
    path(
        'accounts/password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
        name='password_reset_confirm',
    ),
    path(
        'accounts/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete',
    ),
    path('api/', include(router.urls)),
    path('api/dashboard/summary/', dashboard_summary_api, name='api-dashboard-summary'),
    path('api/dashboard/charts/', charts_data_api, name='api-dashboard-charts'),
    path('api/reports/tax-summary/', tax_summary_api, name='api-tax-summary'),
    path('api/auth/csrf/', csrf_view, name='api-auth-csrf'),
    path('api/auth/login/', login_view, name='api-auth-login'),
    path('api/auth/register/', register_view, name='api-auth-register'),
    path('api/auth/google/', google_login_view, name='api-auth-google'),
    path('api/auth/logout/', logout_view, name='api-auth-logout'),
    path('api/auth/me/', me_view, name='api-auth-me'),
    path('', include('dashboard.urls')),
    path('agencies/', include('agencies.urls')),
    path('shifts/', include('shifts.urls')),
    path('licences/', include('licences.urls')),
    path('expenses/', include('expenses.urls')),
    path('reports/', include('reports.urls')),
]
