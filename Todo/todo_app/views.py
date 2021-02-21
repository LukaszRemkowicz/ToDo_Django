from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

# Create your views here.
from .forms import UserLoginForm, RegisterForm


def todo(request):
    return render(request, 'todo_list.html')


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
            return render(request, 'Todo/todo_list.html')
    form = UserLoginForm
    return render(request, 'Todo/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('/')
        else:
            messages.error(request, 'wrong parameters')
    else:
        form = RegisterForm
    return render(request, 'Todo/register.html', {'form': form})
