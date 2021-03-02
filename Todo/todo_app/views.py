from random import randint

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .forms import UserLoginForm, RegisterForm, Todo_list, ShareForm
from .models import TodoDetails, SharedRelationModel, TodoList

from .decorators import redirect_authorised_user, redirect_notauthorised_user, fake_user

import csv


def shared_view(request, username):
    todo_id = request.GET.get('todo')
    specific_todo_list(request, request.user)
    form = Todo_list
    todolist = TodoDetails.objects.filter(id=todo_id)
    content = {'form': form, 'todo_list': todolist, 'todo_id': todo_id}

    return render(request, 'Todo/spec_todo.html', content)


def delete_todo(request, username):
    user = request.user.id
    todo_id = int(request.GET.get('todo'))
    try:
        todo = TodoDetails.objects.get(id=todo_id, user_id=user).delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except ObjectDoesNotExist:
        messages.error(request, f'there is no Todo list with ID="{todo_id}"')

        return redirect('account')


def delete_share(request, username):
    user = User.objects.get(id=request.user.id)
    todo_post_name = TodoDetails.objects.get(todo_name=request.GET.get('todo'), user_id=user.id)

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
                                   f'There is no relate beetween your "{todo_post_name}" '
                                   f'List and {user_with_privilages.username}')
                    return redirect('account')

            except ObjectDoesNotExist:
                messages.error(request, f'There is no user with addres email {email_addres}')
                return redirect(request.META.get('HTTP_REFERER'))
    content = {'form': form, 'todo_name': todo_post_name}
    return render(request, 'Todo/take_share.html', content)


def sharing_todo(request, username):
    form = ShareForm
    todo_id = request.GET.get('todo')

    if request.method == "POST":
        if form.is_valid:
            email_addres = request.POST.get('text')
            try:
                shared_whom = User.objects.get(email=email_addres)
                user_sharing = User.objects.get(id=request.user.id)
                todo = TodoDetails.objects.get(user_id=user_sharing, todo_id=todo_id)

                try:
                    try_check_db_if_list_shared = SharedRelationModel.objects.get(todo_id=todo.id,
                                                                                  user_id=shared_whom.id)
                    messages.info(request, f'The todo list has been shared before to user {email_addres}')
                    return redirect('account')

                except ObjectDoesNotExist:
                    profile = SharedRelationModel.objects.create(todo_id=todo.todo_id,
                                                                 user_id=shared_whom.id)
                    messages.success(request, 'Succesfull shared')
                    return redirect('account')

            except ObjectDoesNotExist:
                messages.error(request, f'There is no user with addres email {email_addres}')
                return redirect(request.META.get('HTTP_REFERER'))
    todo = TodoList.objects.get(id=todo_id)
    content = {'form': form, 'todo': todo}
    return render(request, 'Todo/sharing_todo.html', content)


def download_CSV(request, username):
    response = HttpResponse(content='text/csv')

    todo_name = request.GET.get('todo')
    user = User.objects.get(id=request.user.id)
    todo = TodoDetails.objects.filter(user_id=user.id, todo_name=todo_name)

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
    todo_id = request.GET.get('todo')
    user = User.objects.get(id=request.user.id)
    todo = TodoDetails.objects.filter(user_id=user.id, todo_id=todo_id).delete()

    return redirect(request.META.get('HTTP_REFERER'))


def deleteCompleted(request, username):
    todo_name = request.GET.get('todo')
    user = User.objects.get(id=request.user.id)
    todo = TodoDetails.objects.filter(complete__exact=True, user_id=user.id, todo_id=todo_name).delete()

    return redirect(request.META.get('HTTP_REFERER'))


@fake_user
def completeTodo(request, todo_id, fake_users=None):
    if fake_users:
        user = User.objects.get(id=int(fake_users))
    else:
        user = User.objects.get(id=request.user.id)
    todo_name = request.GET.get('todo')
    todo = TodoDetails.objects.get(pk=todo_id, user_id=user.id)
    todo.user_id = user.id
    todo.complete = True
    todo.save()

    return redirect(request.META.get('HTTP_REFERER'))


@fake_user
def addTodo(request, username, fake_users=None):
    if fake_users:
        user = User.objects.get(id=int(fake_users))
    else:
        user = User.objects.get(id=request.user.id)
    todo_id = request.GET.get('todo')
    user_todo = TodoList.objects.get(id=int(todo_id))
    form = Todo_list(request.POST)
    if form.is_valid():
        text = request.POST['text']
        description = request.POST['description']
        link = request.POST['link']
        if 'https://www.' not in link:
            link = '//' + link
        elif 'https://' not in link:
            link = '//' + link
        user_id = user.id
        todo = TodoDetails.objects.create(text=text, description=description,
                                          link=link, todo_id=user_todo.user_id,
                                          user_id=user_id)

    return redirect(request.META.get('HTTP_REFERER'))


@fake_user
@redirect_notauthorised_user
def specific_todo_list(request, username, fake_users=None):
    if fake_users:
        user = User.objects.get(id=int(fake_users))
    else:
        user = User.objects.get(id=request.user.id)
    todo_id = request.GET.get('todo')
    form = Todo_list
    todo = TodoList.objects.get(id=int(todo_id))
    todocontent = TodoDetails.objects.filter(user_id=user.id)
    content = {'form': form, 'todo_list': todocontent, 'todo_id': todo_id, 'todo': todo}
    return render(request, 'Todo/spec_todo.html', content)


@redirect_notauthorised_user
def create_todo(request):
    form = ShareForm
    user = User.objects.get(id=request.user.id)

    if request.method == 'POST' and form.is_valid:

        todo = TodoList.objects.create(user_id=user.id, name=request.POST.get('text'))

        return redirect('account')
    else:
        content = {'form': form}
        return render(request, 'Todo/todo.html', content)


@redirect_notauthorised_user
def user_account(request):
    user = User.objects.get(id=request.user.id)
    todo_query = TodoList.objects.filter(user_id=user.id)
    shared_todo = SharedRelationModel.objects.filter(user=user.id)
    list_of_shared_todos = []
    for shared in shared_todo:
        todo_shared = TodoList.objects.filter(id=shared.todo_id)
        list_of_shared_todos.append(todo_shared[0])

    content = {'todo_list': todo_query, 'list_of_shared_todos': list_of_shared_todos}
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
