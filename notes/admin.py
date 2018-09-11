from django.contrib import admin
from .models import Note, Comment


admin.site.register(Comment)
admin.site.register(Note)
