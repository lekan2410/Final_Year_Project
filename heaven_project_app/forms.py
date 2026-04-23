from django import forms
from django.db import models
from .models import Review_FoodBank, Review_Shelter, Review_Support_Service, Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _




class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text=_('Enter email for verification.'), label=_("Email"))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

        help_texts = {
            'username':_(
            'For privacy, use a nickname. Your username is not your real name.' ),
        }

class EmailVerifcationForm(forms.Form):
    email = forms.EmailField(required=True, help_text= _('Enter email for verification.'), label=_("Email"))  

class EnterUsername(forms.Form):
    username = forms.CharField(required=True, help_text=_('Enter Username'), label=_("Username")) 

class ChangeEmailForm(forms.ModelForm):

    email = forms.EmailField(required=True, help_text= _("Enter new email here"), label=_("Email"))

    class Meta:
        model = User
        fields = ['email']
  

class PasswordForm(forms.Form):
    password = forms.CharField(required=True, 
        help_text=_("Enter your password please"),
        widget=forms.PasswordInput)
        
    re_enter_password = forms.CharField(required=True,
    help_text=_("Re-enter your password please"),
    widget=forms.PasswordInput) 

STAR_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]

YES_NO_CHOICES = [
    (1, _("Yes")),
    (0, _("No"))
]

class ReviewFoodBankForm(forms.ModelForm):
    name = forms.ChoiceField(label=_("Username"))
    rating = forms.ChoiceField(choices = STAR_CHOICES, label=_("Rating"))


    easy_access_q= forms.ChoiceField(choices=YES_NO_CHOICES,
                widget=forms.RadioSelect,
                label=_("Was this service easy to access?"))
    
    staff_q= forms.ChoiceField(choices=YES_NO_CHOICES,
                widget=forms.RadioSelect,
                label=_("Were the staff friendly?"))
    
    recommend_q= forms.ChoiceField(choices=YES_NO_CHOICES,
                widget=forms.RadioSelect,
                label=_("Would you recommend this food bank?"))

    class Meta:
        model = Review_FoodBank
        fields = ['name', 'rating', 'easy_access_q', 'staff_q', 'recommend_q']
    

    # Getting the user username
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated: 
            self.fields["name"].choices = [
            ("Anonymous", "anonymous"),
            (user.username, user.username) ]

class ReviewShelterForm(forms.ModelForm):
    name = forms.ChoiceField(label=_("Username"))
    rating = forms.ChoiceField(choices = STAR_CHOICES, label=_("Rating"))


    easy_access_q= forms.ChoiceField(choices=YES_NO_CHOICES,
                widget=forms.RadioSelect,
                label=_("Was this service easy to access?"))
    
    staff_q= forms.ChoiceField(choices=YES_NO_CHOICES,
                widget=forms.RadioSelect,
                label=_("Were the staff friendly?"))
    
    recommend_q= forms.ChoiceField(choices=YES_NO_CHOICES,
                widget=forms.RadioSelect,
                label=_("Would you recommend this shelter?"))

    class Meta:
        model = Review_Shelter
        fields = ['name', 'rating', 'easy_access_q', 'staff_q', 'recommend_q']
    

    # Getting the user username
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated: 
            self.fields["name"].choices = [
            ("Anonymous", "anonymous"),
            (user.username, user.username) ]


class ReviewSupportServiceForm(forms.ModelForm):
    name = forms.ChoiceField(label=_("Username"))
    rating = forms.ChoiceField(choices = STAR_CHOICES, label=_("Rating"))


    easy_access_q= forms.ChoiceField(choices=YES_NO_CHOICES,
                widget=forms.RadioSelect,
                label=_("Was this service easy to access?"))
    
    staff_q= forms.ChoiceField(choices=YES_NO_CHOICES,
                widget=forms.RadioSelect,
                label=_("Were the staff friendly?"))
    
    recommend_q= forms.ChoiceField(choices=YES_NO_CHOICES,
                widget=forms.RadioSelect,
                label=_("Would you recommend this support service?"))

    class Meta:
        model = Review_Support_Service
        fields = ['name', 'rating', 'easy_access_q', 'staff_q', 'recommend_q']
    

    # Getting the user username
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated: 
            self.fields["name"].choices = [
            ("Anonymous", "anonymous"),
            (user.username, user.username) ]
    


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_image',)
    

# https://www.youtube.com/watch?v=_P_-gum7rio (Profile Picture)

# https://www.geeksforgeeks.org/python/choicefield-django-forms/