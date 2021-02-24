"""Todo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from todo_app import views as todo_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', todo_view.home, name='home'),
    path('login', todo_view.log_in, name='login'),
    path('register/', todo_view.register, name='register'),
    path('todo/', todo_view.todo, name='todo'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('addtodo', todo_view.addTodo, name='addtodo'),
    path('complete/<todo_id>', todo_view.completeTodo, name='complete'),
    path('deletecomplete', todo_view.deleteCompleted, name='deleteCompleted'),
    path('deleteall', todo_view.deleteAll, name='deleteall'),
]
