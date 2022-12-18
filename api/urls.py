from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

app_name = "api"

urlpatterns = [
    # api/notes/
    path('notes/', views.NotesApi.as_view(), name="notes"),

    # api/notes/note34/
    path('notes/note<int:note_id>/', views.NoteAPi.as_view(), name="note"),

    # api/create_user/
    path('create_user/', views.UserCreateApi.as_view(), name="create-user"),

    # api/login/
    path('login/', obtain_auth_token, name="api-login"),

    # api/create_note/
    path('create_note/', views.NoteCreationApi.as_view(), name="create-note"),

    # TODO: DEPRECATE
    # api/comments/
    path('<int:pk>/comments/', views.AllComments.as_view(), name='comments'),

    # api/v2/33/comments/
    path('v2/<int:note_pk>/comments/', views.AllCommentsV2.as_view(), name='comments-v2'),

    # api/comment/4/actions/
    path('comment/<int:pk>/actions/', views.comment_actions, name='comment-actions'),

    # api/comment/4/actions/v2/
    path('comment/<int:comment_pk>/actions/v2/', views.comment_actions_v2, name='comment-actions-v2'),

    # user/get/
    path('user/get/', views.get_user, name='get-user'),

]
