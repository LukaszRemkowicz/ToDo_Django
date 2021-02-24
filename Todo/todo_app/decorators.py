from django.http import HttpResponse
from django.shortcuts import redirect


def redirect_authorised_user(func):
    def wrapper_auth_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('todo')
        else:
            return func(*args, **kwargs)

    return wrapper_auth_user
