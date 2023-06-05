from django.urls import path
from .views import LoginUserView, LogoutUserView, register_view

urlpatterns = [
    path('', LoginUserView.as_view(), name='login'),
    path('registration/', register_view, name='registration'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
]
