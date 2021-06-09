from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

app_name = "api"

urlpatterns = [
    # notes/
    path('notes/', views.NotesApi.as_view(), name="notes"),

    # notes/note34/
    path('notes/note<int:note_id>/', views.NoteAPi.as_view(), name="note"),

    # create_user/
    path('create_user/', views.UserCreateApi.as_view(), name="create-user"),

    # login/
    path('login/', obtain_auth_token, name="api-login"),

    # create_note/
    path('create_note/', views.NoteCreationApi.as_view(), name="create-note"),

    # comments/
    path('<int:pk>/comments/', views.AllComments.as_view(), name='comments'),

    # comments/4/actions/
    path('comment/<int:pk>/actions/', views.comment_actions, name='comment-actions'),

    # user/get/
    path('user/get/', views.get_user, name='get-user'),

]
