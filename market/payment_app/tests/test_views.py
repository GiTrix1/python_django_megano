import json
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import RequestFactory

from market_app.models import Seller, Product, SellerProduct, Category
from app_login.models import Profile
from payment_app.utils import post_method_for_payment_views, get_dict_with_payment_status
from api_for_payment_app.models import PaymentStatusModel
from order_app.models import OrderModel


class PaymentAPIResponseStandartSituation:
    def __init__(self):
        self.status_code = 200

    def json(self):
        return {
            "status": {
                "status_code": "S200",
                "status_description": "Оплата прошла успешно"
            }}


class PaymentAPIResponseWrongCardNumber:
    def __init__(self):
        self.status_code = 200

    def json(self):
        return {
            "status": {
                "status_code": "S404",
                "status_description": "Ошибка: ваша карта не найдена"
            }}


class PaymentAPIResponseWrongCardBalance:
    def __init__(self):
        self.status_code = 200

    def json(self):
        return {
            "status": {
                "status_code": "S403",
                "status_description": "Ошибка: на вашем счете недостаточно средств"
            }}


class CouldntGetDataFromApi:
    def __init__(self):
        self.status_code = 404


class PostMethodForPaymentViewTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test', password='Asdfg54321')
        cls.category = Category.objects.create(title='телефоны', slug='phones', parent=None, activity=True)
        cls.product = Product.objects.create(name='test_product_1', category=cls.category, slug='t_prod_1')
        cls.profile = Profile.objects.create(user=cls.user, full_name='test test test', phone='888888')
        cls.seller = Seller.objects.create(name=cls.user.username, profile=cls.profile, description='test')
        cls.seller_product = SellerProduct.objects.create(product=cls.product, seller=cls.seller, qty=1, price=10)
        PaymentStatusModel.objects.create(status_code='S204', status_description='test desc')
        PaymentStatusModel.objects.create(status_code='S000', status_description='test desc')
        cls.factory = RequestFactory()
        json_order_data = json.dumps({'t_price': 1000, 'products_list': [{'product_id': cls.product.id}],
                                      'order_dict': {'test': 'test'}})
        cls.order_object = OrderModel.objects.create(user=cls.user, json_order_data=json_order_data)

    def setUp(self) -> None:
        self.login_user = self.client.login(username='test', password='Asdfg54321')

    def get_payment_status(self, card_number):
        response = self.factory.post('/payment/pay_my_card/', {'card_number': card_number})
        response.user = self.user
        status = post_method_for_payment_views(response, order_id=self.order_object.id)
        return status

    @patch("requests.get", return_value=PaymentAPIResponseStandartSituation())
    def test_standart_situation(self, mocked):
        status = self.get_payment_status(card_number='1111 1112')
        self.assertEqual(status['status']['status_code'], 'S200')

    @patch("requests.get", return_value=PaymentAPIResponseWrongCardNumber())
    def test_wrong_card_number(self, mocked):
        status = self.get_payment_status(card_number='1111 1111')
        self.assertEqual(status['status']['status_code'], 'S404')

    @patch("requests.get", return_value=PaymentAPIResponseWrongCardBalance())
    def test_wrong_card_balance(self, mocked):
        json_order_data = json.dumps({'t_price': 100000000, 'products_list': [{'product_id': self.product.id}],
                                      'order_dict': {'test': 'test'}})
        self.order_object.json_order_data = json_order_data
        self.order_object.save()
        status = self.get_payment_status(card_number='1111 1112')
        self.assertEqual(status['status']['status_code'], 'S403')

    @patch("requests.get", return_value=PaymentAPIResponseStandartSituation())
    def test_no_products_in_order(self, mocked):
        json_order_data = json.dumps({'t_price': 1000000, 'products_list': [],
                                      'order_dict': {'test': 'test'}})
        self.order_object.json_order_data = json_order_data
        self.order_object.save()
        status = self.get_payment_status(card_number='1111 1112')
        self.assertEqual(status['status']['status_code'], 'S000')

    @patch("requests.get", return_value=CouldntGetDataFromApi())
    def test_couldnt_get_data_from_api(self, mocked):
        wrong_base_url = 'http://127.0.0.1:8000/test'
        card_number = '1111 1112'
        status_dict = get_dict_with_payment_status(base_url=wrong_base_url,
                                                   card_number=card_number,
                                                   order_id=self.order_object.id)

        self.assertEqual(status_dict['status']['status_code'], 'S204')
