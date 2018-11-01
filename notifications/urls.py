from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    # notifications/
    path('', views.new_notification, name="all"),

    # notifications/open/45/
    path('open/<int:notification_id>/', views.make_opened, name="open"),
]
