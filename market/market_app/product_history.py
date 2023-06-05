"""
Модуль содержит класс для работы с историей просмотров пользователя:
  - добавить товар к списку просмотренных товаров;
  - удалить товар из списка просмотренных товаров;
  - узнать, есть ли товар уже в списке просмотренных;
  - получить список просмотренных товаров;
  - получить количество просмотренных товаров.
"""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.db.models import Min

from .models import Product, HistoryView
from utils.utils import CacheCleaner


class HistoryViewOperations:
    """ Класс содержит методы для работы с историей просмотров пользователя """

    def __init__(self, user: User):
        self.user: User = user
        # Идентификатор истории просмотра в кэше
        self.cache_id = f'history_view:{self.user.pk}'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def products(self):
        """
        Возвращает список просмотренных товаров.
        Продукты берутся из кэша. В случае отсутствия в кэше, берутся из базы.
        """

        def _get_products_from_db():
            return Product.objects.filter(histories__user=self.user).order_by('-histories__view_time').\
                annotate(min_price=Min('sellers_products__price'))
        return cache.get_or_set(self.cache_id, _get_products_from_db)

    def count(self) -> int:
        """
        Возвращает количество просмотренных товаров
        """
        return len(self.products())

    def delete_product(self, product: Product):
        """
        Удаляет товар из списка просмотренных
        args:
            product - товар
        """

        # История просмотров изменится - очистим кэш
        with CacheCleaner(self.cache_id):
            HistoryView.objects.filter(user=self.user, product=product).delete()

    def add_product(self, product: Product):
        """
        Добавляет товар к списку просмотренных
        args:
            product - товар
        """

        # История просмотров изменится - очистим кэш
        with CacheCleaner(self.cache_id):
            history_item = HistoryView.objects.filter(user=self.user, product=product).first()
            # Если данный продукт уже просматривали ранее, то обновим время просмотра
            if history_item is not None:
                history_item.save()
            else:
                with transaction.atomic():
                    # По ТЗ в истории просмотра хранится только 20 последних просмотренных
                    # товаров. Если в истории 20 или более товаров, то удалим самый ранний
                    # просмотр.
                    query_set = HistoryView.objects.filter(user=self.user)
                    if len(query_set) >= 20:
                        query_set.earliest('view_time').delete()
                    HistoryView.objects.create(user=self.user, product=product)

    def is_product_in_history(self, product: Product) -> bool:
        """
        Возвращает True, если товар содержится в списке просмотренных
        args:
            product - товар
        """
        return HistoryView.objects.filter(user=self.user, product=product).exists()
