from django.contrib import admin
from .models import Note, Comment, Reply, Tag


admin.site.register(Note)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Reply)
