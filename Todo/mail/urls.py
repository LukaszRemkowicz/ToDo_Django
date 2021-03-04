from django.urls import path
from django.views.generic import TemplateView
from . import views

from .views import RequestPasswordResetEmail, SetNewPasswordView

urlpatterns = [
    path('reset_password/', RequestPasswordResetEmail.as_view(), name='reset_password'),
    path('set_newpassword/<uidb64>/<token>', SetNewPasswordView.as_view(), name='set_newpassword')
]