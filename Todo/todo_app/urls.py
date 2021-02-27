from django.urls import path, re_path
from . import views
from .views import addTodo, specific_todo_list, user_account, deleteCompleted, deleteAll, download_CSV, sharing_todo

urlpatterns = [
    # path('', views.log_in, name='login'),
    # path('', views.register, name='register'),
    # path('', views.todo, name='todo'),
    # path('', addTodo, name='addtodo'),
    path('account/', user_account, name='account'),
    re_path(r'addtodo/(?P<username>[\w-]+)/$', addTodo, name='addtodo'),
    re_path(r'^(?P<username>[\w-]+)/$', specific_todo_list, name='todolist'),
    re_path(r'deletecomplete/(?P<username>[\w-]+)/$', deleteCompleted, name='deleteCompleted'),
    re_path(r'deleteall/(?P<username>[\w-]+)/$', deleteAll, name='deleteall'),
    re_path(r'download_csv/(?P<username>[\w-]+)/$', download_CSV, name='download_csv'),
    re_path(r'share/(?P<username>[\w-]+)/$', sharing_todo, name='share'),

]