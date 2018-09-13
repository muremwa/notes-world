from django.urls import path
from . import views

app_name = "base_account"

urlpatterns = [

    # /index||profile/
    path('', views.AccountIndex.as_view(), name="account-index"),

    # account/signup/
    path('signup/', views.sign_up, name="sign-up"),

    # account/profile/
    path('profile/', views.ProfilePage.as_view(), name="profile"),

    # account/profile/edit/34/
    path('profile/edit/<int:pk>/', views.ProfileEditView.as_view(), name="profile-edit"),

    # account/connect/
    path('connect/', views.ConnectedUser.as_view(), name="connected"),

    # account/connect/user4/send  (ajax)
    path('connect/user<int:id>/send', views.connect, name="connect"),

    # account/connect/request4/accept (ajax)
    path('connect/request<int:id>/accept', views.accept, name="accept"),

    # account/connect/user4/exit  (ajax)
    path('connect/user<int:id>/exit', views.dis_connect, name="exit"),

    # account/connect/request6/deny  (ajax)
    path('connect/request<int:id>/deny', views.deny, name="deny"),

]