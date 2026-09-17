from django.urls import path

from . import views

app_name = "agencies"

urlpatterns = [
    path("", views.AgencyListView.as_view(), name="agency-list"),
    path("new/", views.AgencyCreateView.as_view(), name="agency-create"),
    path("<int:pk>/edit/", views.AgencyUpdateView.as_view(), name="agency-update"),
    path("<int:pk>/delete/", views.AgencyDeleteView.as_view(), name="agency-delete"),
    path("sites/", views.SiteListView.as_view(), name="site-list"),
    path("sites/new/", views.SiteCreateView.as_view(), name="site-create"),
    path("sites/<int:pk>/edit/", views.SiteUpdateView.as_view(), name="site-update"),
    path("sites/<int:pk>/delete/", views.SiteDeleteView.as_view(), name="site-delete"),
]
