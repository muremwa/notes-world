from django.urls import path
from . import views

app_name = "notes"

urlpatterns = [
    # notes/
    path("", views.NoteIndex.as_view(), name="index"),

    # notes/note34/
    path("note<int:pk>/", views.NotePage.as_view(), name="note-page"),

    # notes/new/note/
    path("new/note/", views.NoteCreate.as_view(), name="note-create"),

    # notes/edit/note34/
    path("edit/note<int:pk>/", views.NoteEdit.as_view(), name="note-edit"),

    # notes/delete/note34/
    path("delete/note<int:pk>/", views.NoteDelete.as_view(), name="note-delete"),

    # notes/tag/note34/
    path("tag/note<int:pk>/", views.add_tags_to_note, name='add-tag'),

    # notes/collaboration/
    path("collaborations/", views.Collaborations.as_view(), name="collaborate_page"),

    # notes/edit/collaboration/note34/
    path("edit/collaboration/note<int:pk>/", views.CollaboratorsEdit.as_view(), name="edit-collaborators"),

    # notes/new/collaborator/note34/user34/
    path("new/collaborator/note<int:note_id>/user<int:user_id>/", views.add_collaborator, name="add-collaborator"),

    # notes/new/collaborator/note34/user34/
    path("delete/collaborator/note<int:note_id>/user<int:user_id>/", views.rm_collaborator, name="remove-collaborator"),

    # notes/note34/make_collaborative/
    path("note<int:note_id>/make_collaborative/", views.make_collaborative, name="make-collaborative"),

    # notes/note34/undo_collaborative/
    path("note/note<int:note_id>/undo_collaborative/", views.undo_collaborative, name="undo-collaborative"),

    # notes/new/note34/comment/
    path("new/note<int:note_id>/comment/", views.CommentProcessing.as_view(), name="comment"),

    # notes/delete/comment23/
    path("delete/comment<int:comment_id>/", views.delete_comment, name="comment-delete"),

    # notes/get/comment/34/ or notes/get/reply/12/
    path("get/<what>/<int:what_id>/", views.get_comment_or_reply, name="get-comment-reply"),

    # notes/comments/comment34/edit/
    path("comments/comment<int:comment_id>/edit/", views.EditComment.as_view(), name="edit-comment"),

    # notes/comment/34/reply/
    path("comment/<int:comment_id>/reply/", views.CommentReply.as_view(), name="reply-comment"),

    # notes/reply/12/edit/ or notes/reply/12/delete/
    path("reply/<int:reply_id>/<option>/", views.ReplyActions.as_view(), name="reply-actions"),
]
