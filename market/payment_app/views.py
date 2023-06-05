from django.shortcuts import render
from django.views import View

from .utils import post_method_for_payment_views


class PayMyCardView(View):
    """
    Представления для вывода страницы payment.html и получения информации с нее
    """
    def get(self, request, order_id) -> render:
        return render(request, 'payment/payment.html')

    def post(self, request, order_id) -> render:
        payment_status = post_method_for_payment_views(request, order_id)
        return render(request, 'payment/progressPayment.html',
                      context={'message_status': payment_status['status']['status_description'],
                               'status_code': payment_status['status']['status_code']})


class PaySomeoneCardView(View):
    """
    Представления для вывода страницы paymentsomeone.html и получения информации с нее
    """
    def get(self, request, order_id) -> render:
        return render(request, 'payment/paymentsomeone.html')

    def post(self, request, order_id) -> render:
        payment_status = post_method_for_payment_views(request, order_id)
        return render(request, 'payment/progressPayment.html',
                      context={'message_status': payment_status['status']['status_description'],
                               'status_code': payment_status['status']['status_code']})
