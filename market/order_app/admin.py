from django.contrib import admin
from order_app.models import OrderModel


class OrderAdmin(admin.ModelAdmin):
    pass


admin.site.register(OrderModel, OrderAdmin)
