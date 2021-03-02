from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import redirect

from .models import TodoDetails, SharedRelationModel, TodoList


def redirect_authorised_user(func):
    def wrapper_auth_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('account')
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


def fake_user(func):
    def wrapper_func(request, *args, **kwargs):
        todo_id = request.GET.get('todo')
        todo_user = TodoList.objects.get(id=todo_id)
        if request.user.id != todo_user.user_id:
            try:
                reletaed_todo = SharedRelationModel.objects.get(todo=int(todo_id), user=request.user.id)
                return func(request, fake_users=todo_user.user_id, *args, **kwargs)
            except ObjectDoesNotExist:
                return func(request, *args, **kwargs)
        else:
            return func(request, *args, **kwargs)

    return wrapper_func
