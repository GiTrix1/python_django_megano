"""market URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from app_login.views import (UserPasswordResetCompleteView,
                             UserPasswordResetConfirmView,
                             UserPasswordResetDoneView,
                             UserResetPasswordView)

urlpatterns = [
                  path('', include('market_app.urls')),
                  path('i18n', include('django.conf.urls.i18n')),
                  path('admin/', admin.site.urls),
                  path('settings/', include('app_settings.urls')),
                  path('comparison/', include('compare_app.urls')),
                  path('login/', include('app_login.urls')),
                  path('password-reset/', UserResetPasswordView.as_view(), name='password_reset'),
                  path('password-reset/done/', UserPasswordResetDoneView.as_view(), name='password_reset_done'),
                  path('reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(),
                       name='password_reset_confirm'),
                  path('reset/done/', UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
                  path('cart/', include('app_cart.urls')),
                  path('account/', include('app_profile.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
