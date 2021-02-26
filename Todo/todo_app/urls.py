from django.urls import path, re_path
from . import views
from .views import addTodo, specific_todo_list, user_account

urlpatterns = [
    # path('', views.log_in, name='login'),
    # path('', views.register, name='register'),
    # path('', views.todo, name='todo'),
    # path('', addTodo, name='addtodo'),
    re_path(r'(?P<username>[\w-]+)/([\w@%.=]+<string>)+/addtodo', addTodo, name='addtodo'),
    path('', addTodo, name='addtodo'),
    re_path(r'^(?P<username>[\w-]+)/$', specific_todo_list, name='todolist'),

]