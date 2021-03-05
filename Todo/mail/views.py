from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from validate_email import validate_email
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import threading
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError

from django.contrib.auth.models import User

from Todo.settings import DEFAULT_FROM_EMAIL

from django.conf import settings

from .forms import NewPasswordForm

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail


# class SendActivationLink(View):
#     def get(self, request):
#         return render(request, 'mail/reset_password.html')
#
#     def post(self, request):
#
#         email = request.POST.get('email')
#         context = {
#             'values': request.POST
#         }
#
#         if not validate_email(email):
#             messages.error(request, 'Please supply a valid email')
#             return render(request, 'mail/reset_password.html', context)
#
#         current_site = get_current_site(request)
#         user = User.objects.filter(email=email)
#         if user.exists():
#             email_subject = '[Reset your Password]'
#             message = render_to_string('mail/reset_mail.html',
#                                        {
#                                            'domain': current_site.domain,
#                                            'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
#                                            'token': PasswordResetTokenGenerator().make_token(user[0])
#                                        }
#                                        )
#
#             email_message = EmailMessage(
#                 email_subject,
#                 message,
#                 DEFAULT_FROM_EMAIL,
#                 [email]
#             )
#
#             EmailThread(email_message).start()
#
#             messages.success(request, 'We have sent you an email to reset your password')
#
#         return render(request, 'mail/reset_password.html')


class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'mail/reset_password.html')

    def post(self, request):

        email = request.POST.get('email')
        context = {
            'values': request.POST
        }

        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            return render(request, 'mail/reset_password.html', context)

        current_site = get_current_site(request)
        user = User.objects.filter(email=email)
        if user.exists():
            email_subject = '[Reset your Password]'
            message = render_to_string('mail/reset_mail.html',
                                       {
                                           'domain': current_site.domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                                           'token': PasswordResetTokenGenerator().make_token(user[0])
                                       }
                                       )

            email_message = EmailMessage(
                email_subject,
                message,
                DEFAULT_FROM_EMAIL,
                [email]
            )

            EmailThread(email_message).start()

            messages.success(request, 'We have sent you an email to reset your password')

        return render(request, 'mail/reset_password.html')


class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        form = NewPasswordForm
        context = {
            'uidb64': uidb64,
            'token': token,
            'form': form,
        }

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(
                    request, 'Password reset link, is invalid, please request a new one')
                return render(request, 'mail/reset_mail.html')

        except DjangoUnicodeDecodeError as identifier:
            messages.success(
                request, 'Invalid link')
            return render(request, 'mail/reset_mail.html')

        return render(request, 'mail/reset_password_complete.html', context)

    def post(self, request, uidb64, token):
        form = NewPasswordForm
        context = {
            'uidb64': uidb64,
            'token': token,
            'has_error': False,
            'form': form,
        }

        password = request.POST.get('password')
        password2 = request.POST.get('retype_password')
        if len(password) < 6:
            messages.add_message(request, messages.ERROR,
                                 'passwords should be at least 6 characters long')
            context['has_error'] = True
        if password != password2:
            messages.add_message(request, messages.ERROR,
                                 'passwords don`t match')
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'mail/reset_password_complete.html', context)

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(
                request, 'Password reset success, you can login with new password')

            return redirect('login')

        except DjangoUnicodeDecodeError as identifier:
            messages.error(request, 'Something went wrong')
            return render(request, 'mail/reset_password_complete.html', context)
