import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Profile

from .widgets import UserFileInput, PasswordInputWithViewToggle


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(max_length=200, widget=PasswordInputWithViewToggle(attrs={"class": "form-control"}))


class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(
        max_length=200,
        widget=PasswordInputWithViewToggle(attrs={"class": "form-control"}),
        label='Password'
    )
    password2 = forms.CharField(
        max_length=200,
        widget=PasswordInputWithViewToggle(attrs={"class": "form-control"}),
        label='Confirm password'
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')

    def clean_username(self):
        data = self.cleaned_data['username']
        if re.search(r'@', data):
            raise ValidationError(_('no @ signs on username'), code="at_sign")
        return data


# profile edit form
class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ("pen_name", "occupation", "gender", "image")
        widgets = {
            'pen_name': forms.TextInput(attrs={"class": "form-control"}),
            'occupation': forms.TextInput(attrs={"class": "form-control"}),
            'gender': forms.Select(attrs={"class": "form-select"}),
            'image': UserFileInput()
        }


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)
        widgets = {
            'username': forms.TextInput(attrs={"class": "form-control"}),
            'first_name': forms.TextInput(attrs={"class": "form-control"}),
            'last_name': forms.TextInput(attrs={"class": "form-control"}),
            'email': forms.EmailInput(attrs={"class": "form-control"})
        }

    def clean_username(self):
        data = self.cleaned_data['username']
        if re.search(r'@', data):
            raise ValidationError(_('no @ signs on username'), code="at_sign")
        return data


class PasswordChangeFormWithToggle(PasswordChangeForm):
    old_password = forms.CharField(widget=PasswordInputWithViewToggle(attrs={"class": "form-control"}))
    new_password1 = forms.CharField(widget=PasswordInputWithViewToggle(attrs={"class": "form-control"}))
    new_password2 = forms.CharField(widget=PasswordInputWithViewToggle(attrs={"class": "form-control"}))
