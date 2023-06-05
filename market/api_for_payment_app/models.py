from django.db import models
from django.utils.translation import gettext_lazy as _


class CardModel(models.Model):
    card_number = models.CharField(max_length=9, verbose_name=_('номер карты'))
    balance = models.FloatField(verbose_name=_('баланс карты'))

    class Meta:
        verbose_name = _('номер карты')
        verbose_name_plural = _('номера карт')

    def __str__(self):
        return self.card_number


class PaymentStatusModel(models.Model):
    status_code = models.CharField(max_length=5, verbose_name=_('код статуса'))
    status_description = models.CharField(max_length=100, verbose_name=_('описание статуса'))

    class Meta:
        verbose_name = _('статус оплаты')
        verbose_name_plural = _('статусы оплаты')

    def __str__(self):
        return self.status_code
