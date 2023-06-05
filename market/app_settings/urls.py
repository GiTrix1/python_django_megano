from django.urls import path

from .views import SettingsView

urlpatterns = [
    path('', SettingsView.as_view(), name='settings'),
]
