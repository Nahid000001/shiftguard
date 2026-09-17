from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="index"),
    path("charts/", views.ChartsView.as_view(), name="charts"),
]
