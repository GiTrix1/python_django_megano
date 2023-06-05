import json
import os

from dotenv import dotenv_values

from app_settings.models import SiteSettings
from market.settings import BASE_DIR


def get_settings_from_json():
    """Функция загружает настройки для сайта."""
    path_to_env = os.path.join(BASE_DIR, '../', '.env')
    config = dotenv_values(path_to_env)

    with open(config['PATH_SETTINGS_CONFIG'], encoding='utf-8') as file:
        settings_config = json.load(file)
        return settings_config


def get_setting_from_db(field_name):
    """Функция получает значение заданного поля из модели настроек"""
    setting = SiteSettings.objects.first()
    field_value = getattr(setting, field_name)
    return field_value
