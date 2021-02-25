from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .forms import UserLoginForm, RegisterForm, Todo_list
from .models import Todo

from .decorators import redirect_authorised_user, redirect_notauthorised_user


def deleteAll(request):
    user = User.objects.get(id=request.user.id)
    todo = Todo.objects.filter(user_id=user.id).delete()

    return redirect('todo')


def deleteCompleted(request):
    user = User.objects.get(id=request.user.id)
    todo = Todo.objects.filter(complete__exact=True, user_id=user.id).delete()

    return redirect('todo')


def completeTodo(request, todo_id):
    user = User.objects.get(id=request.user.id)
    todo = Todo.objects.get(pk=todo_id, user_id=user.id)
    todo.user_id = user.id
    todo.complete = True
    todo.save()

    return redirect('todo')


@require_POST
def addTodo(request):
    form = Todo_list(request.POST)
    user = User.objects.get(id=request.user.id)
    if form.is_valid():
        todo = Todo()
        todo.text = request.POST['text']
        todo.description = request.POST['description']
        todo.link = request.POST['link']
        if 'https://www.' not in todo.link:
            todo.link = '//' + todo.link
        elif 'https://' not in todo.link:
            todo.link = '//' + todo.link
        todo.user_id = user.id
        todo.save()

    return redirect('todo')


@redirect_authorised_user
def home(request):
    return render(request, 'home.html')


@redirect_notauthorised_user
def todo(request):
    form = Todo_list
    user = User.objects.get(id=request.user.id)
    todolist = Todo.objects.filter(user_id=user.id)
    content = {'form': form, 'todo_list': todolist}
    return render(request, 'Todo/todo_list.html', content)


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
            return render(request, 'Todo/todo_list.html', content)
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
