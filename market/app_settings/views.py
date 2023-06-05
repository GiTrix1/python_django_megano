from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View

from app_settings.forms import SettingsForm
from app_settings.models import SiteSettings


class SettingsView(View):
    """Класс-представление страницы настроек"""
    # Translators: разделы кэша на странице настроек
    sections = (('banners', _('Баннеры')),
                ('seller_cache_time', _('Кэш страницы продавца')),
                ('sellers_products_top_cache_time', _('Кэш топ товаров продавца')),
                ('all', _('Общий кэш'))
                )

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request):
        """
        Функция обрабатывающая GET запрос, возвращает страницу настроек с формой
        настроек и кнопками сброса кэша.
        """
        settings = SiteSettings.objects.first()
        settings_form = SettingsForm(instance=settings)
        return render(request, 'app_settings/settings.html', context={'settings_forms': settings_form,
                                                                      'sections': self.sections,
                                                                      })

    def post(self, request):
        """
        Функция обрабатывающая POST запрос со страницы настроек, сохраняет данные формы
        настроек или ловит нажатие одной из кнопок сброса кэша.
        """
        settings = SiteSettings.objects.first()
        settings_form = SettingsForm(request.POST, instance=settings)

        for section in self.sections:
            value = request.POST.get(section)
            if value:
                if value == 'all':
                    # Сброс всего кэша
                    cache.clear()
                    break

                # Сброс кэша определенного раздела
                cache.delete(value)
                break

        if settings_form.is_valid():
            settings.save()
        return HttpResponseRedirect(reverse('settings'))
