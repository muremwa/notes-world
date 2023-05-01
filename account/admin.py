from django.contrib import admin
from .models import Profile, Connection

# Register your models here
admin.site.register(Profile)


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_filter = ('conn_sender', 'conn_receiver', 'approved')
    list_display = ('conn_sender', 'conn_receiver', 'approved')
    actions = ['disapprove_connections', 'approve_connections']

    def disapprove_connections(self, request, queryset):
        if self.has_change_permission(request):
            queryset.update(approved=False)
            self.message_user(request, 'Disapproved selected connections')

    def approve_connections(self, request, queryset):
        if self.has_change_permission(request):
            queryset.update(approved=True)
            self.message_user(request, 'Approved selected connections')
