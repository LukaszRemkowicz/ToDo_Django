from django.urls import path, re_path
from .views import addTodo, specific_todo_list, user_account, deleteCompleted, deleteAll, \
    download_CSV, sharing_todo, delete_share, delete_todo, shared_list, delete_view_share

urlpatterns = [

    path('account/', user_account, name='account'),
    re_path(r'addtodo/(?P<username>[\w-]+)/$', addTodo, name='addtodo'),
    re_path(r'^(?P<username>[\w-]+)/$', specific_todo_list, name='todolist'),
    re_path(r'deletecomplete/(?P<username>[\w-]+)/$', deleteCompleted, name='deleteCompleted'),
    re_path(r'deleteall/(?P<username>[\w-]+)/$', deleteAll, name='deleteall'),
    re_path(r'download_csv/(?P<username>[\w-]+)/$', download_CSV, name='download_csv'),
    re_path(r'^share/(?P<username>[\w-]+)/$', sharing_todo, name='share'),
    re_path(r'delete_sharing/(?P<username>[\w-]+)/$', delete_share, name='delete_sharing'),
    re_path(r'delete_todo/(?P<username>[\w-]+)/$', delete_todo, name='delete_todo'),
    re_path(r'shared_list/(?P<username>[\w-]+)/$', shared_list, name='shared_list'),
    re_path(r'delete_view_share/(?P<username>[\w-]+)/$', delete_view_share, name='delete_view_share'),

]