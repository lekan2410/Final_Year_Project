from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text= 'Enter email for verification.')

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

        help_texts = {
            'username':  'For privacy, use a nickname.'
            ' Your username does not need to be your real name. ', 
        }