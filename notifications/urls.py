from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    # notifications/
    path('', views.new_notification, name="all"),

    # notifications/open/45/
    path('open/<int:notification_id>/', views.make_opened, name="open"),

    # notification/delete/45/
    path('delete/<int:notification_id>/', views.delete_notification, name="delete"),

    # notifications/delete/bulk/
    path('delete/bulk/', views.bulk_delete_notifications, name='bulk-delete'),
]
