import json
from datetime import date
from typing import Union

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.http import HttpResponseRedirect

from app_cart.models import AuthShoppingCart
from app_cart.utils import delete_product_auth_user
from market_app.models import ProductImage, SellerProduct
from app_settings.models import SiteSettings
from order_app.models import OrderModel


def add_data_in_order_cache(**kwargs) -> None:
    """
    Функция добавления данных в кэш заказа
    """
    order_dict = cache.get('order') or {}
    for key, value in kwargs.items():
        order_dict[key] = value
    cache.set('order', order_dict)


def delete_data_from_order_cache(*args) -> None:
    """
    Функция удаления данных из кэша заказа
    """
    order_dict = cache.get('order') or {}
    for key in args:
        order_dict.pop(key)
    cache.set('order', order_dict)


def is_one_seller(products_id) -> bool:
    """
    Функция проверяет, единый ли продавец у всех товаров, добавленных в корзину
    """
    sellers_set = set()
    for product_id in products_id:
        seller = SellerProduct.objects.select_related('product', 'seller').get(product=product_id).seller
        sellers_set.add(seller)
    if len(sellers_set) == 1:
        return True
    else:
        return False


def get_data_from_cart_for_auth_user(request) -> HttpResponseRedirect or [int, list, bool]:
    """
    Функция для формирования данных заказа. Считается общая сумма, формируется список продуктов
    """
    products_in_cart = AuthShoppingCart.objects.select_related('products').filter(user=request.user)
    total_price = 0
    products = []
    products_id = []
    for product in products_in_cart:
        product_dict = {}
        try:
            product_dict['product_id'] = product.products.id
            product_dict['image'] = ProductImage.objects.filter(product=product.products.id).first().image.url
            product_dict['category'] = product.products.category.title
            product_dict['description'] = product.products.description
            product_dict['qty'] = product.count
            product_dict['price'] = float(product.price) * float(product_dict['qty'])
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('del_product_cart'), {'product_id': product.products.id})
        products.append(product_dict)
        total_price += product_dict['price']
        products_id.append(product.products.id)

    one_seller = is_one_seller(products_id)

    return total_price, products, one_seller


def calculate_delivery_cost(order_data, one_seller) -> int:
    """
    Функция для вычисления стоимости доставки заказа
    """
    settings = SiteSettings.objects.all().first()
    delivery_cost = 0
    if order_data['order_dict']['delivery'] == 'express':
        delivery_cost = int(settings.express_delivery_cost)
    elif order_data['order_dict']['delivery'] == 'ordinary':
        if order_data['t_price'] < settings.min_amount_for_free_delivery or not one_seller:
            delivery_cost = int(settings.ordinary_delivery_cost)

    return delivery_cost


def check_cache(order_dict) -> Union[None, HttpResponseRedirect]:
    """
    Функция для проверки наличия данных шагов 1-3 оформления заказа в кэше. Без них не даст перейти на 4 шаг
    """
    if order_dict:
        if {'full_name', 'delivery', 'pay'}.issubset(set(order_dict.keys())):
            return None
    return HttpResponseRedirect(reverse('order_step_1'))


def prepare_order_data(request, order_dict) -> dict:
    """
    Функция добавляет стоимость доставки к общей сумме заказа, дату заказа и статус оплаты в данные заказа
    """
    total_price, products, one_seller = get_data_from_cart_for_auth_user(request)

    order_data = {'t_price': total_price, 'products_list': products, 'order_dict': order_dict}
    order_data['delivery_cost'] = calculate_delivery_cost(order_data, one_seller)
    order_data['t_price'] += order_data['delivery_cost']
    order_data['order_dict']['added_date'] = date.today()
    order_data['order_dict']['payment_status'] = 'Не оплачено'

    return order_data


def create_order_object(user, order_data) -> OrderModel:
    """
    Функция создания заказа в БД
    """
    json_order_data = json.dumps(order_data, default=str)
    order = OrderModel.objects.create(user=user, json_order_data=json_order_data)

    return order


def clear_user_cart(request) -> None:
    """
    Функция очищения корзины пользователя после создания заказа в БД
    """
    products_in_cart = AuthShoppingCart.objects.select_related('products').filter(user=request.user)
    for product in products_in_cart:
        delete_product_auth_user(request, product.products.id)
