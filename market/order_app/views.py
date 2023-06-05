import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from app_login.models import Profile
from order_app.utils import add_data_in_order_cache, check_cache, prepare_order_data, create_order_object,\
    clear_user_cart
from order_app.models import OrderModel


class OrderStepOneView(LoginRequiredMixin, View):
    """
    Представления для первого шага оформления товара
    """

    login_url = '/login/'

    def get(self, request) -> render:
        try:
            profile = Profile.objects.get(user=request.user)
            user_email = User.objects.get(id=request.user.id).email
            context = {'full_name': profile.full_name,
                       'phone': profile.phone,
                       'email': user_email}

        except ObjectDoesNotExist:
            return HttpResponse(_('Не удалось получить данные пользователя'))

        return render(request, 'order/order_step_1.html', context=context)

    def post(self, request) -> HttpResponseRedirect:
        data_dict = {'full_name': request.POST.get('name'),
                     'phone': request.POST.get('phone'),
                     'mail': request.POST.get('mail')}
        add_data_in_order_cache(**data_dict)

        return HttpResponseRedirect(reverse('order_step_2'))


class OrderStepTwoView(View):
    """
    Представление для второго шага оформления товара
    """
    def get(self, request) -> render:
        context = {}
        order_dict = cache.get('order') or {}
        if 'delivery' in order_dict.keys():
            context = {'delivery': order_dict['delivery'],
                       'city': order_dict['city'],
                       'address': order_dict['address']}
        return render(request, 'order/order_step_2.html', context)

    def post(self, response) -> HttpResponseRedirect:
        data_dict = {'delivery': response.POST.get('delivery'),
                     'city': response.POST.get('city'),
                     'address': response.POST.get('address')}
        add_data_in_order_cache(**data_dict)

        return HttpResponseRedirect(reverse('order_step_3'))


class OrderStepThreeView(View):
    """
    Представление для третьего шага оформления заказа
    """
    def get(self, request) -> render:
        context = {}
        order_dict = cache.get('order') or {}
        if 'pay' in order_dict.keys():
            context = {'pay': order_dict['pay']}
        return render(request, 'order/order_step_3.html', context)

    def post(self, response) -> HttpResponseRedirect:
        add_data_in_order_cache(**{'pay': response.POST.get('pay')})

        return HttpResponseRedirect(reverse('order_step_4'))


class OrderStepFourView(View):
    """
    Представление для четвертого шага оформления товара
    """
    def get(self, request) -> render:
        order_dict = cache.get('order')

        returned_check_cache_data = check_cache(order_dict)
        if returned_check_cache_data:
            return returned_check_cache_data

        order_data = prepare_order_data(request, order_dict)

        return render(request, 'order/order_step_4.html', context=order_data)

    def post(self, request) -> HttpResponseRedirect:
        order_dict = cache.get('order')
        order_data = prepare_order_data(request, order_dict)

        order = create_order_object(request.user, order_data)

        return HttpResponseRedirect(reverse('order_detail', kwargs={'order_id': order.id}))


class OrderView(View):
    """
    Представление для вывода уже оформленного и добавленного в БД заказа
    """
    def get(self, request, order_id) -> render:
        order_object = OrderModel.objects.get(user=request.user, id=order_id)
        order_data = json.loads(order_object.json_order_data)
        clear_user_cart(request)
        context = {'order_id': order_id, 'order_data': order_data,
                   'pay_method': order_data['order_dict']['pay']}
        return render(request, 'order/oneorder.html', context=context)
