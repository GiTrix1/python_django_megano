from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PaymentStatusModel, CardModel


def check_status(card_number: str, price: int) -> PaymentStatusModel:
    """
    Функция, в которой проверяется статус оплаты заказа
    """
    try:
        card = CardModel.objects.get(card_number=card_number)
        if price == 0:
            status = PaymentStatusModel.objects.get(status_code='S000')
        elif card.balance < price:
            status = PaymentStatusModel.objects.get(status_code='S403')
        else:
            status = PaymentStatusModel.objects.get(status_code='S200')
        return status

    except ObjectDoesNotExist:
        status = PaymentStatusModel.objects.get(status_code='S404')
        return status


class PaymentAPIView(APIView):
    """
    API представление для возврата JSON данных со статусом оплаты
    """
    def get(self, request, card_number: str, price: int) -> Response:
        status = check_status(card_number=card_number, price=price)
        return Response({'status': {'status_code': status.status_code,
                                    'status_description': status.status_description}})
