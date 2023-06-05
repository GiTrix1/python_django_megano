from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from market_app.models import Product
from .services import add_product_in_cache, get_products_for_compare, remove_product_from_cache


def add_product_for_compare_view(request, product_id: int) -> HttpResponseRedirect or HttpResponse:
    """
    Это представление реализует добавление товара в список для сравнения, хранящийся к кэше
    """
    if request.method == "GET":
        try:
            product = Product.objects.select_related('category').get(id=product_id)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(_('Продукт не найден'))

        compare_object = cache.get('compare_object')
        if compare_object:
            if not compare_object['category_for_compare'] == product.category:
                return render(request, 'comparison.html', context={'products_for_compare_dict': None,
                                                                   'isFalseCategory': True})

            add_product_in_cache(compare_object, product)

        else:
            cache.set('compare_object',
                      {
                          'category_for_compare': product.category,
                          'products_list': [product_id]
                      }
                      )

        return HttpResponseRedirect('/comparison/')


def remove_good_for_compare_view(request, product_id: int) -> HttpResponseRedirect or HttpResponse:
    """
    Данное представление удаляет товар из списка товаров для сравнения в кэше по переданному product_id
    """
    compare_object = cache.get('compare_object')

    if compare_object:
        remove_product_from_cache(compare_object, product_id)
        return HttpResponseRedirect('/comparison/')
    else:
        return HttpResponseBadRequest(_('Ошибка: данной записи в кэше не существует'))


def get_products_list_for_compare_view(request) -> render:
    """
    Представление для вывода данных о товарах, добавленных в список для сравнения
    """
    compare_object = cache.get('compare_object')
    if compare_object is None:
        products_for_compare_dict = None
    else:
        products_for_compare_dict = get_products_for_compare(compare_object)
    return render(request, 'comparison.html', context={'products_for_compare_dict': products_for_compare_dict,
                                                       'isFalseCategory': False})
