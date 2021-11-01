from django.forms import ModelForm
from django.forms import ValidationError
from django import forms
from datetime import datetime
from .models import *
from django.contrib.auth.forms import UserCreationForm,UserChangeForm ,PasswordChangeForm
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class CompanySignUpForm(ModelForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    
    class Meta:
        model = User
        fields = ('name', 'email','password', 'confirm_password')

    def __init__(self, *args, **kwargs):
        super(CompanySignUpForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(CompanySignUpForm, self).clean()
        password = cleaned_data["password"]
        confirm_password = cleaned_data["confirm_password"]
        if(password!=confirm_password):
            raise ValidationError("Password did not match")

    def save(self,commit=True):
        user = super(CompanySignUpForm,self).save(commit=False)
        user.email=self.cleaned_data['email']
        user.save()
        return user   

class Job_Post(ModelForm):
    class Meta:
          model = Jobs
          fields=("role","location","job_description","phone_number")

    def __init__(self,user,*args,**kwargs):
        super(Job_Post,self).__init__(*args,**kwargs)