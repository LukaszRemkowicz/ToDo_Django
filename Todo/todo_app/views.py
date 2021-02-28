from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .forms import UserLoginForm, RegisterForm, Todo_list, ShareForm
from .models import Todo, SharedRelationModel

from .decorators import redirect_authorised_user, redirect_notauthorised_user

import csv


def delete_share(request, username):
    user = User.objects.get(id=request.user.id)
    todo_post_name = Todo.objects.get(todo_name=request.GET.get('todo'))

    form = ShareForm

    if request.method == "POST":
        if form.is_valid:
            email_addres = request.POST.get('text')
            try:
                user_with_privilages = User.objects.get(email=email_addres)

                try:

                    relation = SharedRelationModel.objects.get(todo__todo_name=todo_post_name,
                                                               user__id=user_with_privilages.id).delete()
                    messages.success(request, 'Succesfull deleted related')
                    return redirect('account')

                except ObjectDoesNotExist:
                    messages.error(request,
                                   f'There is no relate beetween your Todo List and {user_with_privilages.username}')
                    return redirect('account')

            except ObjectDoesNotExist:
                messages.error(request, f'There is no user with addres email {email_addres}')
                return redirect(request.META.get('HTTP_REFERER'))
    content = {'form': form, 'todo_name': todo_post_name}
    return render(request, 'Todo/take_share.html', content)


def sharing_todo(request, username):
    form = ShareForm
    todo_name = request.GET.get('todo')
    if request.method == "POST":
        if form.is_valid:
            email_addres = request.POST.get('text')
            try:
                shared_whom = User.objects.get(email=email_addres)
                user_sharing = User.objects.get(id=request.user.id)
                todo = Todo.objects.get(user_id=user_sharing, todo_name=todo_name)

                try:
                    try_check_db_if_list_shared = SharedRelationModel.objects.get(todo_id=todo.id,
                                                                                  user_id=shared_whom.id)
                    messages.info(request, f'The todo list has been shared before to user {email_addres}')
                    return redirect('account')

                except ObjectDoesNotExist:
                    profile = SharedRelationModel.objects.create(todo_id=todo.id,
                                                                 user_id=shared_whom.id)
                    messages.success(request, 'Succesfull shared')
                    return redirect('account')

            except ObjectDoesNotExist:
                messages.error(request, f'There is no user with addres email {email_addres}')
                return redirect(request.META.get('HTTP_REFERER'))
    content = {'form': form, 'todo_name': todo_name}
    return render(request, 'Todo/sharing_todo.html', content)


def download_CSV(request, username):
    response = HttpResponse(content='text/csv')

    todo_name = request.GET.get('todo')
    user = User.objects.get(id=request.user.id)
    todo = Todo.objects.filter(user_id=user.id, todo_name=todo_name)

    writer = csv.writer(response)
    writer.writerow(['Todo', 'Todo_Description', 'todo_name', 'Todo_added_date', 'Todo_completed'])
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
    todo = Todo.objects.filter(user_id=user.id, todo_name=todo_name).delete()

    return redirect(request.META.get('HTTP_REFERER'))


def deleteCompleted(request, username):
    todo_name = request.GET.get('todo')
    user = User.objects.get(id=request.user.id)
    todo = Todo.objects.filter(complete__exact=True, user_id=user.id, todo_name=todo_name).delete()

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
        todo.todo_name = todo_name
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

    if request.method == 'POST':
        todo = Todo.objects.create(user_id=user.id, todo_name=request.POST.get('todo_name'))

        return redirect('account')
    else:

        return render(request, 'Todo/todo.html')


@redirect_notauthorised_user
def user_account(request):
    user = User.objects.get(id=request.user.id)
    todo_query = Todo.objects.filter(user_id=user.id)
    # todo_list = todo_list.values_list('todo_name')
    content = {'todo_list': todo_query}
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
