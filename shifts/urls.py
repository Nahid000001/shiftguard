from django.urls import path

from . import views

app_name = "shifts"

urlpatterns = [
    path("", views.ShiftListView.as_view(), name="list"),
    path("new/", views.ShiftCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.ShiftUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.ShiftDeleteView.as_view(), name="delete"),
]
