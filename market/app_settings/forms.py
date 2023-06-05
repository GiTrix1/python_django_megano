from django import forms

from .models import SiteSettings


class SettingsForm(forms.ModelForm):
    """Класс формы для внесения настроек сайта"""

    class Meta:
        model = SiteSettings
        fields = '__all__'
