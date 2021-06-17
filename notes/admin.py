from django.contrib import admin
from .models import Note, Comment, Reply, Tag


admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Reply)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    exclude = ('last_modified', 'last_modifier')
    list_display = ('title', 'user', 'privacy', 'collaborative')
