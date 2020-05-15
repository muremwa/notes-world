from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationModelAdmin(admin.ModelAdmin):
    list_display = ('to_user', 'get_created', 'seen')
