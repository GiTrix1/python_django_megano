from django.contrib import admin
from .models import CardModel, PaymentStatusModel


class CardAdmin(admin.ModelAdmin):
    pass


class PaymentStatusAdmin(admin.ModelAdmin):
    pass


admin.site.register(CardModel, CardAdmin)
admin.site.register(PaymentStatusModel, PaymentStatusAdmin)
