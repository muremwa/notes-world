from django.urls import path
from . import views

app_name = "base_account"

urlpatterns = [
    
    # /index||profile/
    path('', views.AccountIndex.as_view(), name="account-index"),

    # account/signup/
    path('signup/', views.SignUp.as_view(), name="sign-up"),

    # account/profile/
    path('profile/', views.ProfilePage.as_view(), name="profile"),

    # account/profile/edit/34/
    path('profile/edit/<int:pk>/', views.ProfileEditView.as_view(), name="profile-edit"),
    
]