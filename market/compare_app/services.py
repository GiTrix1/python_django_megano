from typing import Union

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.translation import gettext_lazy as _

from market_app.models import Product, CharacteristicValue, ProductImage


def add_product_in_cache(compare_object: dict, product) -> None:
    """
    Функция реализует функционал добавления товара в кэш и проверку, чтобы кол-во товаров в корзине не превышало два
    """
    if len(compare_object['products_list']) < 2:
        compare_object['products_list'].append(product.id)
        cache.set('compare_object', compare_object)
    else:
        compare_object['products_list'].pop(0)
        compare_object['products_list'].append(product.id)
        cache.set('compare_object', compare_object)


def remove_product_from_cache(compare_object: dict, product_id: str) -> Union[None, HttpResponseBadRequest]:
    """
    Функция реализует функционал удаления товара из кэша
    """
    try:
        compare_object['products_list'].remove(product_id)
        cache.set('compare_object', compare_object)
        if len(cache.get('compare_object')['products_list']) < 1:
            cache.delete('compare_object')
    except ValueError:
        return HttpResponseBadRequest(_('Ошибка: не удалось удалить товар из списка товаров для сравнения'))


def formation_initial_dict_for_product(product_id: str, compare_dict: dict) -> Union[dict, HttpResponse]:
    """
    Функция формирует изначальный словарь для продукта, в который после будут добавляться его характеристики
    """
    try:
        product = Product.objects.get(id=product_id)
        image_path = ProductImage.objects.filter(product=product).first().image
        compare_dict[product.name] = {'image_path': image_path,
                                      'product_id': product.id,
                                      'characteristics': dict()}
    except ObjectDoesNotExist:
        return HttpResponse(_('Ошибка: не удалось сформировать словарь для сравнения товаров'))
    return product, compare_dict


def create_characteristics_dict(product) -> dict:
    """
    Функция создает словарь групп характеристик и списков - характеристика - значение характеристики.
    """
    existing_groups = list()
    characteristics_dict = dict()

    characteristics = CharacteristicValue.objects.select_related('characteristic').filter(product=product)
    if not characteristics:
        raise ObjectDoesNotExist

    for characteristic_value in characteristics:
        characteristic_list = [characteristic_value.characteristic.characteristic_name, characteristic_value.value]
        group_name = characteristic_value.characteristic.group.group_name
        if group_name in existing_groups:
            characteristics_dict[group_name].append(characteristic_list)
        else:
            characteristics_dict[group_name] = [characteristic_list]
            existing_groups.append(group_name)
    return characteristics_dict


def get_products_for_compare(compare_object: dict) -> dict:
    """
    Данная функция собирает все необходимые данные в словарь, который впоследствии будет передан в шаблон.

    Структура словаря:
    { Название товара :
        {
            'image_path' (str) - путь до фото товара,
            'product_id' (str) - id товара,
            'characteristics' (dict) :
                {
                    Группа характеристик :
                    [
                        [
                            Название характеристики,
                            Значение характеристики
                        ],
                        ....
                    ],
                    ....
                }
        }
    }
    """

    products_for_compare_dict = dict()
    for product_id in compare_object['products_list']:
        product, products_for_compare_dict = formation_initial_dict_for_product(product_id=product_id,
                                                                                compare_dict=products_for_compare_dict)
        products_for_compare_dict[product.name]['characteristics'] = create_characteristics_dict(product=product)

    return products_for_compare_dict
