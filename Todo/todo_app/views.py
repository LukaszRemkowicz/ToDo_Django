from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .forms import UserLoginForm, RegisterForm, Todo_list, ShareForm
from .models import Todo, Profile

from .decorators import redirect_authorised_user, redirect_notauthorised_user

import csv


def sharing_todo(request, username):
    form = ShareForm
    todo_name = request.GET.get('todo')
    if request.method == "POST":
        if form.is_valid:
            email_addres = request.POST.get('text')
            try:
                user = User.objects.get(email=email_addres)
            except ObjectDoesNotExist:
                messages.error(request, f'There is no user with addres email {email_addres}')
                return redirect(request.META.get('HTTP_REFERER'))
    content = {'form': form, 'todo_name': todo_name}
    return render(request, 'Todo/sharing_todo.html', content)



def download_CSV(request, username):
    response = HttpResponse(content='text/csv')

    todo_name = request.GET.get('todo')
    user = User.objects.get(id=request.user.id)
    todo = Todo.objects.filter(user_id=user.id, todo_link=todo_name)

    writer = csv.writer(response)
    writer.writerow(['Todo', 'Todo_Description', 'Todo_link', 'Todo_added_date', 'Todo_completed'])
    for todo in todo.values_list('text', 'description', 'link', 'date_added', 'complete'):
        todo_elements = list(todo)
        if todo_elements[2] == '//':
            todo_elements[2] = ''
        elif todo_elements[0] == '//':
            todo_elements
        writer.writerow(todo_elements)

    response['Content-Disposition'] = 'attachment; filename="to_list.csv"'

    return response


def deleteAll(request, username):
    todo_name = request.GET.get('todo')
    user = User.objects.get(id=request.user.id)
    todo = Todo.objects.filter(user_id=user.id, todo_link=todo_name).delete()

    return redirect(request.META.get('HTTP_REFERER'))


def deleteCompleted(request, username):
    todo_name = request.GET.get('todo')
    user = User.objects.get(id=request.user.id)
    todo = Todo.objects.filter(complete__exact=True, user_id=user.id, todo_link=todo_name).delete()

    return redirect(request.META.get('HTTP_REFERER'))


def completeTodo(request, todo_id):
    todo_name = request.GET.get('todo')
    user = User.objects.get(id=request.user.id)
    todo = Todo.objects.get(pk=todo_id, user_id=user.id)
    todo.user_id = user.id
    todo.complete = True
    todo.save()

    return redirect(request.META.get('HTTP_REFERER'))


def addTodo(request, username):
    todo_name = request.GET.get('todo')
    form = Todo_list(request.POST)
    user = User.objects.get(id=request.user.id)
    if form.is_valid():
        todo = Todo()
        todo.text = request.POST['text']
        todo.description = request.POST['description']
        todo.link = request.POST['link']
        todo.todo_link = todo_name
        if 'https://www.' not in todo.link:
            todo.link = '//' + todo.link
        elif 'https://' not in todo.link:
            todo.link = '//' + todo.link
        todo.user_id = user.id
        todo.save()

    return redirect(request.META.get('HTTP_REFERER'))


@redirect_notauthorised_user
def specific_todo_list(request, username):
    todo_name = request.GET.get('todo')
    form = Todo_list
    user = User.objects.get(id=request.user.id)
    todolist = Todo.objects.filter(user_id=user.id)
    content = {'form': form, 'todo_list': todolist, 'todo_name': todo_name}
    return render(request, 'Todo/spec_todo.html', content)


@redirect_notauthorised_user
def create_todo(request):
    user = User.objects.get(id=request.user.id)
    todo = Profile.objects.get(user_id=user.id)
    if request.method == 'POST':
        todo_name = request.POST.get('todo_name')
        todo.todo_link = todo.todo_link + ";" + todo_name
        todo.save()

        return redirect('account')
    else:

        return render(request, 'Todo/todo.html')


@redirect_notauthorised_user
def user_account(request):
    user = User.objects.get(id=request.user.id)
    todo_query = Profile.objects.get(user_id=user.id).todo_link
    todo_list = todo_query.split(';')
    # todo_list = todo_list.values_list('todo_link')
    content = {'todo_list': todo_list}
    return render(request, 'Todo/account.html', content)


@redirect_authorised_user
def home(request):
    return render(request, 'home.html')


# @redirect_notauthorised_user
# def todo(request):
#     form = Todo_list
#     user = User.objects.get(id=request.user.id)
#     todolist = Todo.objects.filter(user_id=user.id)
#     content = {'form': form, 'todo_list': todolist}
#     return render(request, 'Todo/todo_list.html', content)


@redirect_authorised_user
def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if not user:
            messages.info(request, 'username OR password is incorrect')
            return redirect('/')
        else:
            login(request, user)
            form = Todo_list
            content = {'form': form}
            return render(request, 'home.html', content)
    form = UserLoginForm
    return render(request, 'Todo/login.html', {'form': form})


@redirect_authorised_user
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
        else:
            messages.error(request, form.errors)
    else:
        form = RegisterForm
    return render(request, 'Todo/register.html', {'form': form})
