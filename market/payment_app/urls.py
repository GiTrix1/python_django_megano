from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import PayMyCardView, PaySomeoneCardView


urlpatterns = [
    path('pay_my_card/<int:order_id>/', csrf_exempt(PayMyCardView.as_view()), name='pay_my_card'),
    path('pay_someone_card/<int:order_id>/', csrf_exempt(PaySomeoneCardView.as_view()), name='pay_someone_card'),
]
