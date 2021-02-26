from django.urls import path, re_path
from . import views
from .views import addTodo, specific_todo_list, user_account, deleteCompleted, deleteAll

urlpatterns = [
    # path('', views.log_in, name='login'),
    # path('', views.register, name='register'),
    # path('', views.todo, name='todo'),
    # path('', addTodo, name='addtodo'),
    path('account/', user_account, name='account'),
    re_path(r'addtodo/(?P<username>[\w-]+)/$', addTodo, name='addtodo'),
    re_path(r'^(?P<username>[\w-]+)/$', specific_todo_list, name='todolist'),
    path('deletecomplete', deleteCompleted, name='deleteCompleted'),
    path('deleteall', deleteAll, name='deleteall'),

]