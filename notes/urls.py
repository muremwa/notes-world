from django.urls import path
from . import views

app_name = "notes"

urlpatterns = [
    # notes/
    path("", views.NoteIndex.as_view(), name="index"),

    #notes/note34/
    path("note<int:pk>/", views.NotePage.as_view(), name="note-page"),

    # notes/new/note/
    path("new/note/", views.NoteCreate.as_view(), name="note-create"),

    # notes/new/note34/
    path("edit/note<int:pk>/", views.NoteEdit.as_view(), name="note-edit"),

    # notes/delete/note34/
    path("delete/note<int:pk>/", views.NoteDelete.as_view(), name="note-delete"),

    # notes/collaboration/
    path("collaborations/", views.Collaborations.as_view(), name="collaborate_page"),
]