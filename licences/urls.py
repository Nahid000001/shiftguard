from django.urls import path

from . import views

app_name = "licences"

urlpatterns = [
    path("", views.LicenceListView.as_view(), name="list"),
    path("new/", views.LicenceCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.LicenceUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.LicenceDeleteView.as_view(), name="delete"),
]
