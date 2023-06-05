"""
Модуль для работы с баннерами, отображающимися на главной странице сайта.
На главной странице отображается три случайных баннера, баннеры кэшируются
на время, полученное из настроек сайта. При добавлении или удалении баннера
кэш сбрасывается.
"""
import random
from typing import List

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save

from app_settings.utils import get_setting_from_db
from market_app.models import Banner


def get_banner_cache_time() -> int:
    """
    Возвращает время кэширования баннеров на главной странице из настроек сайта
    """
    banner_cache_time = get_setting_from_db('banner_cache_time')
    return banner_cache_time


def get_banners_list() -> List:
    """
    Возвращает список из случайных баннеров. Количество берется из конфига.
    Баннеры берутся из кэша. В случае отсутствия в кэше, берутся из базы.
    """

    def _get_banners_from_db() -> List:
        """ Возвращает список из случайных баннеров из БД """
        banner_number = get_setting_from_db('banner_number')
        try:
            return random.sample(list(Banner.objects.all()), banner_number)
        except ValueError:
            # На случай, если баннеров в базе меньше запрашиваемого количества
            return list(Banner.objects.all())

    return cache.get_or_set('banners', _get_banners_from_db, get_banner_cache_time())


def reset_banners_cache(**kwargs):
    """ Очищает кэш баннеров """
    cache.delete('banners')


# Регистрируем функцию очистки кэша баннеров как функцию-приемник
# сигналов post_save и post_delete
post_save.connect(reset_banners_cache, sender=Banner)
post_delete.connect(reset_banners_cache, sender=Banner)
