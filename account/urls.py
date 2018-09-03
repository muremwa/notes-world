from django.urls import path
from . import views

app_name = "base_account"

urlpatterns = [
    
    # /index||profile/
    path('', views.index, name="account-index"),

    # account/signup/
    path('signup/', views.signUp, name="sign-up"),

    # account/profile/
    path('profile/', views.profile, name="profile"),

    # account/profile/edit/34/
    path('profile/edit/<int:pk>/', views.ProfileEditView.as_view(), name="profile-edit"),
    
]