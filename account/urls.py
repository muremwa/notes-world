from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .forms import LoginForm

app_name = "base_account"

urlpatterns = [

    # /index||profile/
    path('', views.AccountIndex.as_view(), name="account-index"),

    # account/signup/
    path('signup/', views.SignUp.as_view(), name="sign-up"),

    # account/login/
    path('login/', LoginView.as_view(authentication_form=LoginForm), name='login'),

    # account/logout/
    path('logout/', LogoutView.as_view(), name='logout'),

    # account/profile/
    path('profile/', views.ProfilePage.as_view(), name="profile"),

    # account/profile/edit/34/
    path('profile/edit/<int:pk>/', views.ProfileEditView.as_view(), name="profile-edit"),

    # account/user4/edit/
    path('user<int:pk>/edit/', views.ProfileUserEdit.as_view(), name='user-edit'),

    # account/user4/change-password/
    path('user<int:pk>/change-password/', views.UserPasswordChange.as_view(), name='change-password'),

    # account/connect/
    path('connect/', views.ConnectedUser.as_view(), name="connected"),

    # account/connect/user4/send  (ajax)
    path('connect/user<int:user_id>/send', views.connect, name="connect"),

    # account/user/23/
    path('user/<int:user_id>/', views.ForeignUser.as_view(), name="foreign-user"),

    # account/connect/request4/accept (ajax)
    path('connect/request<int:conn_id>/accept', views.accept, name="accept"),

    # account/connect/user4/exit  (ajax)
    path('connect/user<int:user_id>/exit', views.dis_connect, name="exit"),

    # account/connect/request6/deny  (ajax)
    path('connect/request<int:conn_id>/deny', views.deny, name="deny"),

]
