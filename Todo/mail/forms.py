from django import forms


class NewPasswordForm(forms.Form):
    password = forms.CharField(max_length=50, required=True)
    retype_password = forms.CharField(max_length=50, required=True)
