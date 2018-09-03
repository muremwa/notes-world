from django.urls import path
from . import views

app_name = "notes"

urlpatterns = [
    # notes/
    path("", views.index, name="index"),
]