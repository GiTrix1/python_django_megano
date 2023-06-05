"""
 Модуль, содержащий вспомогательные классы и функции
"""""

from django.core.cache import cache


class CacheCleaner:
    """ Менеджер контекста. При завершении удаляет содержимое кэша по идентификатору cache_id """
    def __init__(self, cache_id: str):
        self.cache_id = cache_id

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            cache.delete(self.cache_id)
