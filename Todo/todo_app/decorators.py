from django.http import HttpResponse
from django.shortcuts import redirect


def redirect_authorised_user(func):
    def wrapper_auth_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return func(request, *args, **kwargs)

    return wrapper_auth_user


def redirect_notauthorised_user(func):
    def wrapper_unauth_user(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        else:
            return func(request, *args, **kwargs)

    return wrapper_unauth_user
