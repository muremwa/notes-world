from django.contrib import admin
from .models import Note, Comment, Reply


admin.site.register(Comment)
admin.site.register(Note)
admin.site.register(Reply)
