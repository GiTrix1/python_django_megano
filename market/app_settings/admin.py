from django.contrib import admin

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Класс для работы с моделью настроек в админке"""

    def has_add_permission(self, request, obj=None):
        """Запрещает добавление новых настроек"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Запрещает удаление существующих настроек"""
        return False
