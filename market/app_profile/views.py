from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from .utils import active_order, all_user_order
from app_login.models import Profile, ProfileAvatar
from app_profile.forms import ProfileForm
from market_app.product_history import HistoryViewOperations
import re


class AccountView(TemplateView):

    """
    Личный кабинет
    """

    template_name = 'account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with HistoryViewOperations(self.request.user) as history:
            history_view_list = history.products()[:3]
        context['active_menu'] = 'account'
        context['history_view_list'] = history_view_list
        context['profile'] = Profile.objects.get(user_id=self.request.user.id)
        context['oneorder'] = active_order(self.request)
        return context


class ProfileView(View):

    """
    Профиль пользователя
    """

    def get(self, request):

        if request.user.is_authenticated:

            profile_form = ProfileForm()
            return render(request, 'profile.html', context={'profile_form': profile_form,
                                                            'active_menu': 'profile'})
        else:
            return HttpResponseRedirect('/login/')

    def post(self, request):

        profile_form = ProfileForm(request.POST, request.FILES)

        if profile_form.is_valid():

            avatar = profile_form.cleaned_data.pop('avatar')
            new_password1 = profile_form.cleaned_data.pop('new_password1')
            new_password2 = profile_form.cleaned_data.pop('new_password2')

            if avatar:
                ProfileAvatar.objects.create(avatar=avatar, img_name=f'{avatar}')
                profile_avatar = ProfileAvatar.objects.get(img_name=f'{avatar}')
                Profile.objects.filter(user_id=request.user.id).update(
                    avatar=profile_avatar
                )
            elif new_password1 and new_password2:
                user = User.objects.get(id=request.user.id)
                user.set_password(new_password1)
                user.save()
                login(request, user)

            for key in profile_form.cleaned_data.keys():

                if key == 'full_name' and len(profile_form.cleaned_data[key]) != 0:
                    Profile.objects.filter(id=request.user.id).update(full_name=profile_form.cleaned_data[key])

                elif key == 'email' and len(profile_form.cleaned_data[key]) != 0:
                    User.objects.filter(id=request.user.id).update(email=profile_form.cleaned_data[key])

                elif key == 'phone' and len(profile_form.cleaned_data[key]) != 0:
                    pattern = r"\d+"
                    result = re.findall(pattern, profile_form.cleaned_data[key][2:])
                    new_phone = ''.join(result)
                    Profile.objects.filter(id=request.user.id).update(phone=new_phone)

            return HttpResponseRedirect('success/')

        return render(request, 'profile.html', context={'profile_form': profile_form,
                                                        'active_menu': 'profile'})


class ProfileSuccessView(View):

    """
    Профиль пользователя при успешном изменении
    """

    def get(self, request):

        profile_form = ProfileForm()
        return render(request, 'profileSuccess.html', context={'profile_form': profile_form,
                                                               'active_menu': 'profile'})

    def post(self, request):

        profile_form = ProfileForm(request.POST, request.FILES)

        if profile_form.is_valid():

            avatar = profile_form.cleaned_data.pop('avatar')
            new_password1 = profile_form.cleaned_data.pop('new_password1')
            new_password2 = profile_form.cleaned_data.pop('new_password2')

            if avatar:
                ProfileAvatar.objects.create(avatar=avatar, img_name=f'{avatar}')
                profile_avatar = ProfileAvatar.objects.get(img_name=f'{avatar}')
                Profile.objects.filter(user_id=request.user.id).update(
                    avatar=profile_avatar
                )
            elif new_password1 and new_password2:
                user = User.objects.get(id=request.user.id)
                user.set_password(new_password1)
                user.save()
                login(request, user)

            for key in profile_form.cleaned_data.keys():

                if key == 'full_name' and len(profile_form.cleaned_data[key]) != 0:
                    Profile.objects.filter(id=request.user.id).update(full_name=profile_form.cleaned_data[key])

                elif key == 'email' and len(profile_form.cleaned_data[key]) != 0:
                    User.objects.filter(id=request.user.id).update(email=profile_form.cleaned_data[key])

                elif key == 'phone' and len(profile_form.cleaned_data[key]) != 0:
                    pattern = r"\d+"
                    result = re.findall(pattern, profile_form.cleaned_data[key][2:])
                    new_phone = ''.join(result)
                    Profile.objects.filter(id=request.user.id).update(phone=new_phone)

            return HttpResponseRedirect('/account/edit/success/')

        return render(request, 'profile.html', context={'profile_form': profile_form,
                                                        'active_menu': 'profile'})


class HistoryOrderView(TemplateView):

    """
    История заказов пользователя
    """

    template_name = 'historyorder.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'historyorder'
        context['all_order'] = all_user_order(self.request)
        return context


class HistoryViewView(TemplateView):

    """
    История просмотров пользователя
    """

    template_name = 'historyview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with HistoryViewOperations(self.request.user) as history:
            history_view_list = history.products()
        context['active_menu'] = 'historyview'
        context['history_view_list'] = history_view_list
        return context
