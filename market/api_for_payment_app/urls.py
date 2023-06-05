from django.urls import path

from .views import PaymentAPIView


urlpatterns = [
    path('<str:card_number>/<int:price>/', PaymentAPIView.as_view(), name='get payment status'),
]
