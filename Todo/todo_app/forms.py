from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.contrib.auth.models import User


class UserLoginForm(AuthenticationForm):
    fields = ['username', 'password']


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ('username', 'password1', 'password2', 'email')


class Todo_list(forms.Form):
    text = forms.CharField(max_length=40)
    description = forms.CharField(max_length=400, required=False)
    link = forms.CharField(max_length=400, required=False)


class ShareForm(forms.Form):
    text = forms.CharField(max_length=70, required=True)
