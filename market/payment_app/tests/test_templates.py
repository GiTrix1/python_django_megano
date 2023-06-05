import json

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from api_for_payment_app.models import PaymentStatusModel
from order_app.models import OrderModel


class PaymentTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='test user')
        json_order_data = json.dumps({'t_price': 1000, 'products_list': [],
                                      'order_dict': {'payment_status': 'Не оплачено'}})
        cls.order_object = OrderModel.objects.create(user=user, json_order_data=json_order_data)
        PaymentStatusModel.objects.create(status_code='S200', status_description='test desc')
        PaymentStatusModel.objects.create(status_code='S001', status_description='test desc')

    def test_correct_template_in_payment(self):
        pay_my_card_get = self.client.get(reverse('pay_my_card', kwargs={'order_id': self.order_object.id}))
        pay_someone_card_get = self.client.get(reverse('pay_someone_card', kwargs={'order_id': self.order_object.id}))
        pay_my_card_post = self.client.post(reverse('pay_my_card', kwargs={'order_id': self.order_object.id}),
                                            {'card_number': '1111 1112'})
        pay_someone_card_post = self.client.post(reverse('pay_someone_card',
                                                         kwargs={'order_id': self.order_object.id}),
                                                 {'card_number': '1111 1112'})

        self.assertTemplateUsed(pay_my_card_get, 'payment/payment.html')
        self.assertTemplateUsed(pay_someone_card_get, 'payment/paymentsomeone.html')
        self.assertTemplateUsed(pay_my_card_post, 'payment/progressPayment.html')
        self.assertTemplateUsed(pay_someone_card_post, 'payment/progressPayment.html')
