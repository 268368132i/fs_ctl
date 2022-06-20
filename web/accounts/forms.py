from django import forms
from django.contrib.auth.models import User
from .models import UserProfileInfo
from exchange.models import ConfUser

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username','email','password')

class ConfUserInfoForm(forms.ModelForm):
    class Meta():
        model = ConfUser
