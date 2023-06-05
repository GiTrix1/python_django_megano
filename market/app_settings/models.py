from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    """Модель настроек сайта"""
    site_name = models.CharField(max_length=255, verbose_name=_('название сайта'))
    phone_number1 = models.CharField(max_length=255, verbose_name=_('номер телефона 1'))
    phone_number2 = models.CharField(max_length=255, verbose_name=_('номер телефона 2'))
    address = models.CharField(max_length=255, verbose_name=_('адрес'))
    banner_number = models.PositiveSmallIntegerField(verbose_name=_('количество баннеров'))
    stopping_sales = models.BooleanField(default=False, verbose_name=_('остановка продаж'))
    banner_cache_time = models.PositiveIntegerField(verbose_name=_('кэш баннеров'))
    total_cache_time = models.PositiveIntegerField(verbose_name=_('общий кэш'))
    seller_cache_time = models.PositiveIntegerField(verbose_name=_('время кэша продавцов'))
    sellers_products_top_cache_time = models.PositiveIntegerField(verbose_name=_('время кэша продавцов'))
    sellers_products_top_number = models.PositiveSmallIntegerField(
        verbose_name=_('количество популярных товаров продавца'))
    common_products_top_number = models.PositiveSmallIntegerField(
        verbose_name=_('количество популярных товаров главной страницы'))
    num_reviews_per_page = models.PositiveIntegerField(verbose_name=_('количество отзывов на странице'))
    num_products_per_page = models.PositiveIntegerField(verbose_name=_('количество товаров на странице'))
    ordinary_delivery_cost = models.PositiveIntegerField(verbose_name=_('стоимость обычной доставки'))
    min_amount_for_free_delivery = models.PositiveIntegerField(
        verbose_name=_('минимальная сумма для бесплатной обычной доставки'))
    express_delivery_cost = models.PositiveIntegerField(verbose_name=_('стоимость экспресс доставки'))

    def __str__(self):
        return 'Настройки сайта'

    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.pk = self.__class__.objects.first().pk
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Настройка сайта')
        verbose_name_plural = _('Настройки сайта')
