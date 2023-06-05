from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('заказчик'))
    json_order_data = models.JSONField(verbose_name=_('данные заказа в формате JSON'))
    activity = models.BooleanField(default=True, verbose_name=_('статус активности'))
    objects = models.Manager()

    class Meta:
        verbose_name = _('заказ')
        verbose_name_plural = _('заказы')

    def __str__(self):
        return f'{self.user} - {self.activity}'
