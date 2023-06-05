from django.contrib import admin
from .models import AuthShoppingCart


class AuthShoppingCartAdmin(admin.ModelAdmin):
    pass


admin.site.register(AuthShoppingCart, AuthShoppingCartAdmin)
