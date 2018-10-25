from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
import re

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2',)

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


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)

    def clean_username(self):
        data = self.cleaned_data['username']
        if re.search(r'@', data):
            raise ValidationError(_('no @ signs on username'), code="at_sign")
        return data
