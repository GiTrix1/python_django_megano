from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppSettingsConfig(AppConfig):
    """Класс конфигурации приложения настроек сайта"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_settings'
    verbose_name = _('настройки сайта')
