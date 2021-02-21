from django.urls import path
from . import views
from .views import log_in

urlpatterns = [
    path('', views.log_in, name='login'),
    path('', views.register, name='register'),
    path('', views.todo, name='todo'),
]