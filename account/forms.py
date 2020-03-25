import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2',)
        widgets = {
            'username': forms.TextInput(attrs={"class": "form-control"}),
        }

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
            'gender': forms.Select(attrs={"class": "form-control"}),
            'image': forms.ClearableFileInput(attrs={"class": "form-control"})
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
