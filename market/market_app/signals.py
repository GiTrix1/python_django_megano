from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from market_app.models import Seller


@receiver(post_save, sender=Seller)
def reset_seller_cache(created, instance, **kwargs):
    """
    Функция сбрасывает кэш продавца и его топ товаров при изменении данных продавца
    """
    if not created:
        seller_cache_key = f"seller_detail_{instance.pk}"
        sellers_top_cache_key = f"sellers_top_{instance.pk}"
        cache.delete(seller_cache_key)
        cache.delete(sellers_top_cache_key)
