import datetime

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.html import escape
from django.core.mail import send_mail

from validate_email import validate_email

from .forms import UserLoginForm, RegisterForm, Todo_list, ShareForm
from .models import TodoDetails, SharedRelationModel, TodoList
from mail.utils import PasswordResetTokenGenerator
from .decorators import redirect_authorised_user, redirect_notauthorised_user, fake_user
from Todo.settings import DEFAULT_FROM_EMAIL

import csv


@redirect_notauthorised_user
def delete_view_share(request, username):
    todo_id = int(request.GET.get('todo'))
    user = request.user.id
    todo = SharedRelationModel.objects.get(todo=todo_id, user=user).delete()
    todo = SharedRelationModel.objects.filter(todo=todo_id)
    if not todo:
        todo = TodoList.objects.get(id=todo_id)
        todo.shared = False
        todo.save()
    return redirect(request.META.get('HTTP_REFERER'))


def shared_list(request, username):
    todo_id = int(request.GET.get('todo'))
    todos = SharedRelationModel.objects.filter(todo=todo_id)
    todos_list = []

    for todo in todos:
        try:
            user = User.objects.get(id=todo.user_id)
            todos_list.append(user.email)
        except ObjectDoesNotExist:
            todo.delete()
            pass

    content = {'todos': todos_list,
               'todo_id': todo_id}

    return render(request, 'Todo/shared_list.html', content)


@redirect_notauthorised_user
def delete_todo(request, username):
    user = request.user.id
    todo_id = int(request.GET.get('todo'))
    try:
        todo = TodoList.objects.get(id=todo_id, user_id=user).delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except ObjectDoesNotExist:
        messages.error(request, f'there is no Todo list with ID="{todo_id}"')

        return redirect('account')


@redirect_notauthorised_user
def delete_share(request, username):
    user = User.objects.get(id=request.user.id)
    todo_post_name = TodoList.objects.get(id=int(request.GET.get('todo')), user_id=user.id)
    form = ShareForm

    if request.method == "POST":
        if form.is_valid:
            email_addres = request.POST.get('text')
            try:
                user_with_privilages = User.objects.get(email=email_addres)

                try:

                    relation = SharedRelationModel.objects.get(todo__name=todo_post_name.name,
                                                               user__id=user_with_privilages.id).delete()
                    relation = SharedRelationModel.objects.filter(todo=int(request.GET.get('todo')))
                    if not relation:
                        todo_post_name.shared = False
                    todo_post_name.save()
                    messages.success(request, 'Succesfull deleted related')
                    return redirect('account')

                except ObjectDoesNotExist:
                    messages.error(request,
                                   f'There is no relate beetween your "{todo_post_name}" '
                                   f'List and {user_with_privilages.username}')
                    return redirect('account')

            except ObjectDoesNotExist:
                messages.error(request, f'There is no user with addres email {email_addres}')
                return redirect(request.META.get('HTTP_REFERER'))
    content = {'form': form, 'todo_name': todo_post_name}
    return render(request, 'Todo/take_share.html', content)


@redirect_notauthorised_user
def sharing_todo(request, username):
    form = ShareForm
    todo_id = request.GET.get('todo')

    if request.method == "POST":
        if form.is_valid:
            email_addres = request.POST.get('text')
            if email_addres == request.user.email:
                messages.error(request, f'You cannot share Todo to yourself')
                return redirect(request.META.get('HTTP_REFERER'))
            try:
                shared_whom = User.objects.get(email=email_addres)
                user_sharing = User.objects.get(id=request.user.id)
                todo = TodoList.objects.get(user_id=user_sharing.id, id=int(todo_id))

                try:
                    try_check_db_if_list_shared = SharedRelationModel.objects.get(todo_id=todo.id,
                                                                                  user_id=shared_whom.id)
                    messages.info(request, f'The todo list has been shared before to user {email_addres}')
                    return redirect('account')

                except ObjectDoesNotExist:
                    profile = SharedRelationModel.objects.create(todo_id=todo.id,
                                                                 user_id=shared_whom.id)
                    todo.shared = True
                    todo.save()
                    messages.success(request, 'Succesfull shared')
                    return redirect('account')

            except ObjectDoesNotExist:
                messages.error(request, f'There is no user with addres email {email_addres}')
                return redirect(request.META.get('HTTP_REFERER'))
    todo = TodoList.objects.get(id=int(todo_id))
    content = {'form': form, 'todo': todo}
    return render(request, 'Todo/sharing_todo.html', content)


@redirect_notauthorised_user
@fake_user()
def download_CSV(request, username, fake_users=None):
    if fake_users:
        user = User.objects.get(id=int(fake_users))
    else:
        user = User.objects.get(id=request.user.id)

    response = HttpResponse(content='text/csv')

    todo_name = request.GET.get('todo')
    todo = TodoDetails.objects.filter(user_id=user.id, todo_id=todo_name)

    writer = csv.writer(response)
    writer.writerow(['Todo', 'Todo_Description', 'Link', 'Todo_added_date', 'Todo_completed'])
    for todo in todo.values_list('text', 'description', 'link', 'date_added', 'complete'):
        todo_elements = list(todo)
        copy_list = []
        for col in todo_elements:
            if isinstance(col, datetime.date) or isinstance(col, bool):
                copy_list.append(col)
            elif col == '//':
                copy_list.append('')
            elif ';' in col:
                rep = col.replace(';', ' ').replace(',', ' ')
                copy_list.append(rep)
            else:
                copy_list.append(col)
        writer.writerow(copy_list)

    response['Content-Disposition'] = 'attachment; filename="to_list.csv"'

    return response


@redirect_notauthorised_user
@fake_user()
def deleteAll(request, username, fake_users=None):
    if fake_users:
        user = User.objects.get(id=int(fake_users))
    else:
        user = User.objects.get(id=request.user.id)
    todo_id = request.GET.get('todo')
    todo = TodoDetails.objects.filter(user_id=user.id, todo_id=todo_id).delete()

    return redirect(request.META.get('HTTP_REFERER'))


@redirect_notauthorised_user
@fake_user()
def deleteCompleted(request, username, fake_users=None):
    if fake_users:
        user = User.objects.get(id=int(fake_users))
    else:
        user = User.objects.get(id=request.user.id)
    todo_name = request.GET.get('todo')
    todo = TodoDetails.objects.filter(complete__exact=True, user_id=user.id, todo_id=todo_name).delete()

    return redirect(request.META.get('HTTP_REFERER'))


@redirect_notauthorised_user
@fake_user(is_it_spec_func=True)
def completeTodo(request, todo_id, fake_users=None):
    if fake_users:
        user = User.objects.get(id=int(fake_users))
    else:
        user = User.objects.get(id=request.user.id)
    todo_name = request.GET.get('todo')
    todo = TodoDetails.objects.get(pk=todo_id, user_id=user.id)
    todo.user_id = user.id
    todo.complete = True
    todo.save()

    return redirect(request.META.get('HTTP_REFERER'))


@redirect_notauthorised_user
@fake_user()
def addTodo(request, username, fake_users=None):
    if fake_users:
        user = User.objects.get(id=int(fake_users))
    else:
        user = User.objects.get(id=request.user.id)
    todo_id = request.GET.get('todo')
    user_todo = TodoList.objects.get(id=int(todo_id))
    form = Todo_list(request.POST)
    if form.is_valid():
        text = escape(request.POST['text'])
        description = escape(request.POST['description'])
        link = escape(request.POST['link'])
        if 'https://www.' not in link:
            link = '//' + link
        elif 'https://' not in link:
            link = '//' + link
        user_id = user.id
        todo = TodoDetails.objects.create(text=text, description=description,
                                          link=link, todo_id=user_todo.id,
                                          user_id=user_id)

    return redirect(request.META.get('HTTP_REFERER'))


@redirect_notauthorised_user
@fake_user()
def specific_todo_list(request, username, fake_users=None):
    if fake_users:
        user = User.objects.get(id=int(fake_users))
    else:
        user = User.objects.get(id=request.user.id)
    todo_id = request.GET.get('todo')
    form = Todo_list
    todo = TodoList.objects.get(id=int(todo_id))
    todocontent = TodoDetails.objects.filter(user_id=user.id, todo_id=int(todo_id))
    content = {'form': form, 'todo_list': todocontent, 'todo_id': todo_id, 'todo': todo}
    return render(request, 'Todo/spec_todo.html', content)


@redirect_notauthorised_user
def create_todo(request):
    form = ShareForm
    user = User.objects.get(id=request.user.id)

    if request.method == 'POST' and form.is_valid:

        todo = TodoList.objects.create(user_id=user.id, name=escape(request.POST.get('text')))

        return redirect('account')
    else:
        content = {'form': form}
        return render(request, 'Todo/todo.html', content)


@redirect_notauthorised_user
def user_account(request):
    user = User.objects.get(id=request.user.id)
    todo_query = TodoList.objects.filter(user_id=user.id)
    shared_todo = SharedRelationModel.objects.filter(user=user.id)
    list_of_shared_todos = []
    for shared in shared_todo:
        todo_shared = TodoList.objects.filter(id=shared.todo_id)
        list_of_shared_todos.append(todo_shared[0])

    content = {'todo_list': todo_query, 'list_of_shared_todos': list_of_shared_todos}
    return render(request, 'Todo/account.html', content)


@redirect_authorised_user
def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if not user:
            messages.info(request, 'username OR password is incorrect')
            return redirect('/')

        else:
            if not user.is_active:
                messages.info(request, 'Your account is not active. '
                                       'Please go to your email box and find email with activation link')
                return redirect('/')

            login(request, user)
            form = Todo_list
            content = {'form': form}
            return render(request, 'Todo/account.html', content)
    form = UserLoginForm
    return render(request, 'Todo/login.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        user_id = force_text(urlsafe_base64_decode(uidb64))
        messages.success(request, 'Your account has been activated')
        user = User.objects.get(pk=user_id)

        user.is_active = True
        user.save()

        if not PasswordResetTokenGenerator().check_token(user, token):
            messages.info(
                request, 'Password reset link, is invalid, please request a new one')
            return render(request, 'mail/register.html')

        return redirect('login')

    except DjangoUnicodeDecodeError as identifier:
        messages.success(
            request, 'Invalid link')
        return render(request, 'mail/reset_mail.html')


@redirect_authorised_user
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        email = escape(request.POST.get('email'))
        username = escape(request.POST.get('username').lower())
        password = escape(request.POST.get('password1'))

        try:
            check_email = User.objects.get(email=email)
            messages.error(request, f'Adress email {email} is not avaiable. User created with that email.')
            return redirect('register')

        except ObjectDoesNotExist:
            try:
                user = User.objects.get(username=username)
                messages.error(request, f'Username {username} is not avaiable.')
                return redirect('register')

            except ObjectDoesNotExist:
                pass

        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            form = RegisterForm
            return render(request, 'Todo/registel.html', {'form': form})

        if form.is_valid():

            user = User.objects.create_user(username=username.lower(), email=email)
            user.set_password(password)
            user.is_active = False

            user.save()

            messages.success(request, f'Account created for {username}!')

            current_site = get_current_site(request)
            email_subject = 'Account Activation'
            message = render_to_string('Todo/email_activation.html',
                                       {
                                           'domain': current_site.domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                           'token': PasswordResetTokenGenerator().make_token(user)
                                       }
                                       )

            send_mail(
                subject=email_subject,
                message='',
                from_email=DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=message
            )

            messages.success(request, 'We have sent you an email to activate your account')

            return redirect('login')
        else:
            messages.error(request, form.errors)
    else:
        form = RegisterForm
    return render(request, 'Todo/register.html', {'form': form})
