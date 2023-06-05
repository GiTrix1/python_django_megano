from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import RegisterForm, AuthForm
from .models import Profile
from .utils import transfer_to_auth_cart
from market_app.models import Category
from django.views import View
from django.contrib.auth.views import (LogoutView,
                                       PasswordResetView,
                                       PasswordResetDoneView,
                                       PasswordResetConfirmView,
                                       PasswordResetCompleteView)


categories = Category.objects.all()


class LoginUserView(View):

    """Аунтификация  пользователя"""

    def get(self, request):

        auth_form = AuthForm()
        return render(request, 'login.html', context={'auth_form': auth_form})

    def post(self, request):

        auth_form = AuthForm(request.POST)

        if auth_form.is_valid():

            username = auth_form.cleaned_data['username']
            password = auth_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            transfer_to_auth_cart(request, user)
            login(request, user)
            return HttpResponseRedirect('/')

        return render(request, 'login.html', context={'auth_form': auth_form})


class LogoutUserView(LogoutView):

    """
    Завершение сессии пользователя
    """

    next_page = '/'


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, full_name=f'user_{user.id}')
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            transfer_to_auth_cart(request, user)
            login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = RegisterForm()
    return render(request, 'registration.html', {'form': form,
                                                 'categories': categories})


class UserResetPasswordView(PasswordResetView):

    """
    Начальный этап сброса пароля пользователя
    """

    template_name = 'registration/password_reset.html'


class UserPasswordResetDoneView(PasswordResetDoneView):

    """
    Успешный сброс пароля пользователя
    """

    template_name = 'registration/password_reset_done.html'


class UserPasswordResetConfirmView(PasswordResetConfirmView):

    """
    Ввод нового пороля и подтверждение для сброса пароля пользователя
    """

    template_name = 'registration/password_reset_confirm.html'


class UserPasswordResetCompleteView(PasswordResetCompleteView):

    """
    Завершение сброса пароля и возможность залогиниться с новым паролем
    """

    template_name = 'registration/password_reset_complete.html'
