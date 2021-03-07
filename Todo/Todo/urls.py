from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from todo_app import views as todo_view

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', include('mail.urls')),
    path('', todo_view.log_in, name='login'),
    path('register/', todo_view.register, name='register'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('', include(('todo_app.urls', 'todo_app')), name='todolist'),
    path('complete/<todo_id>/', todo_view.completeTodo, name='complete'),
    path('account/', todo_view.user_account, name='account'),
    path('create_todo', todo_view.create_todo, name='create_todo'),
    path('activate_account/<uidb64>/<token>', todo_view.activate_account, name='activate_account'),

]
