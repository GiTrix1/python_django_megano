import json

from django.test import TestCase
from django.contrib.auth.models import User

from payment_app.utils import create_payment_status_dict, change_payment_status_in_order, check_order,\
    increase_product_purchases
from api_for_payment_app.models import PaymentStatusModel
from order_app.models import OrderModel
from market_app.models import Product, Category, ProductPurchases


class CreatePaymentStatusDictFuncTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        PaymentStatusModel.objects.create(status_code='S200', status_description='test desc')

    def test_ordinary_situation(self):
        status_dict = create_payment_status_dict('S200')

        self.assertEqual(status_dict['status']['status_code'], 'S200')


class ChangePaymentStatusInOrderFuncTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='test user')
        json_order_data = json.dumps({'t_price': 1000, 'products_list': [{'test': 'test'}, {'test_2': 'test'}],
                                      'order_dict': {'payment_status': 'Не оплачено'}})
        cls.order_object = OrderModel.objects.create(user=user, json_order_data=json_order_data)

    def test_ordinary_situation(self):
        change_payment_status_in_order(self.order_object.id)
        order_obj = OrderModel.objects.all().first()
        order_data = json.loads(order_obj.json_order_data)

        self.assertTrue(order_data['order_dict']['payment_status'], 'Оплачено')


class CheckOrderFuncTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        PaymentStatusModel.objects.create(status_code='S000', status_description='test desc')
        PaymentStatusModel.objects.create(status_code='S001', status_description='test desc')
        cls.user = User.objects.create_user(username='test user')
        json_order_data = json.dumps({'t_price': 1000, 'products_list': [{'test': 'test'}, {'test_2': 'test'}],
                                      'order_dict': {'payment_status': 'Не оплачено'}})
        cls.order_object = OrderModel.objects.create(user=cls.user, json_order_data=json_order_data)

    def test_ordinary_situation(self):
        problems_with_order, order_data = check_order(self.order_object.id)

        self.assertIsNone(problems_with_order)
        self.assertTrue(order_data)

    def test_no_products_in_order(self):
        json_order_data = json.dumps({'t_price': 1000, 'products_list': [],
                                      'order_dict': {'payment_status': 'Не оплачено'}})
        self.order_object = OrderModel.objects.create(user=self.user, json_order_data=json_order_data)
        problems_with_order, order_data = check_order(self.order_object.id)

        self.assertIsNotNone(problems_with_order)
        self.assertEqual(problems_with_order['status']['status_code'], 'S000')

    def test_order_does_not_exist(self):
        problems_with_order, order_data = check_order(10)

        self.assertIsNotNone(problems_with_order)
        self.assertEqual(problems_with_order['status']['status_code'], 'S001')


class IncreaseProductPurchasesFuncTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='test user')
        cls.category = Category.objects.create(title='телефоны', slug='phones', parent=None, activity=True)
        cls.product_1 = Product.objects.create(name='test_product_1', category=cls.category, slug='t_prod_1')
        cls.product_2 = Product.objects.create(name='test_product_2', category=cls.category, slug='t_prod_2')
        json_order_data = json.dumps({'t_price': 1000, 'products_list': [{'product_id': cls.product_1.id, 'qty': 1},
                                                                         {'product_id': cls.product_2.id, 'qty': 1}],
                                      'order_dict': {'payment_status': 'Не оплачено'}})
        cls.order_object = OrderModel.objects.create(user=user, json_order_data=json_order_data)

    def test_two_products_and_one_qty(self):
        increase_product_purchases(order_id=self.order_object.id)
        product_purchases = ProductPurchases.objects.all()

        self.assertEqual(len(product_purchases), 2)
        self.assertEqual(product_purchases[0].product, self.product_1)
        self.assertEqual(product_purchases[0].num_purchases, 1)
        self.assertEqual(product_purchases[1].product, self.product_2)
        self.assertEqual(product_purchases[1].num_purchases, 1)
