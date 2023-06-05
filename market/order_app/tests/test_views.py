import json
from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from django.conf import settings
from django.test.client import RequestFactory
from django.utils.module_loading import import_module

from app_login.models import Profile
from order_app.utils import add_data_in_order_cache, delete_data_from_order_cache
from order_app.models import OrderModel
from app_cart.models import AnonimCart, AuthShoppingCart
from market_app.models import Category, Product, Seller, SellerProduct, ProductImage


class OrderStepOneViewTest(TestCase):
    USERNAME = 'test'
    PASSWORD = 'Asdfg54321'
    EMAIL = 'test@mail.ru'
    FULL_NAME = 'test test test'
    PHONE = '1111111111'
    AVATAR = 'test'

    @classmethod
    def setUpTestData(cls):
        cache.clear()
        user = User.objects.create_user(username=cls.USERNAME, email=cls.EMAIL)
        user.set_password(cls.PASSWORD)
        user.save()
        cls.profile = Profile.objects.create(user=user,
                                             full_name=cls.FULL_NAME,
                                             phone=cls.PHONE)

    def setUp(self) -> None:
        self.client.login(username=self.USERNAME, password=self.PASSWORD)

    def test_get_method_user_is_authenticated(self):
        resp = self.client.get(reverse('order_step_1'))
        context = resp.context

        self.assertEqual(context['full_name'], self.FULL_NAME)
        self.assertEqual(context['phone'], self.PHONE)
        self.assertEqual(context['email'], self.EMAIL)

    def test_post_method(self):
        resp = self.client.post(reverse('order_step_1'), {'name': self.FULL_NAME,
                                                          'phone': self.PHONE,
                                                          'mail': self.EMAIL})
        order_dict = cache.get('order')

        self.assertTrue(order_dict)
        self.assertEqual(order_dict['full_name'], self.FULL_NAME)
        self.assertRedirects(resp, '/order/step2/')


class OrderStepTwoViewTest(TestCase):
    DELIVERY = 'ordinary'
    CITY = 'Воронеж'
    ADDRESS = 'test address'

    def test_get_method(self):
        resp = self.client.get(reverse('order_step_2'))

        self.assertEqual(resp.status_code, 200)

    def test_get_method_with_params(self):
        params_dict = {'delivery': self.DELIVERY, 'city': self.CITY, 'address': self.ADDRESS}
        add_data_in_order_cache(**params_dict)

        resp = self.client.get(reverse('order_step_2'))
        delete_data_from_order_cache(*params_dict.keys())
        context = resp.context

        self.assertIsNotNone(context)
        self.assertEqual(context['city'], self.CITY)

    def test_post_method(self):
        resp = self.client.post(reverse('order_step_2'), {'delivery': self.DELIVERY,
                                                          'city': self.CITY,
                                                          'address': self.ADDRESS})
        order_dict = cache.get('order')

        self.assertEqual(order_dict['address'], self.ADDRESS)
        self.assertRedirects(resp, '/order/step3/')


class OrderStepThreeViewTest(TestCase):
    PAY = 'someone'

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='test user step 3', email='step_3@mail.ru')
        user.set_password('Asdfg54321')
        user.save()

    def test_get_method(self):
        resp = self.client.get(reverse('order_step_3'))

        self.assertEqual(resp.status_code, 200)

    def test_get_method_with_params(self):
        add_data_in_order_cache(**{'pay': self.PAY})
        resp = self.client.get(reverse('order_step_3'))
        delete_data_from_order_cache(*['pay'])
        context = resp.context

        self.assertIsNotNone(context)
        self.assertEqual(context['pay'], self.PAY)

    def test_post_method(self):
        cache.set('order', {'full_name': 'test', 'delivery': 'express', 'city': 'test', 'address': 'test',
                            'phone': 'test', 'mail': 'test', 'pay': 'test'})
        self.client.login(username='test user step 3', password='Asdfg54321')
        resp = self.client.post(reverse('order_step_3'), {'pay': self.PAY})
        order_dict = cache.get('order')

        self.assertEqual(order_dict['pay'], self.PAY)
        self.assertRedirects(resp, '/order/step4/')


class OrderStepFourViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test user', password='Asdfg54321')
        cls.profile = Profile.objects.create(user=cls.user, full_name='test test test', phone='888888')
        cls.category = Category.objects.create(title='телефоны', slug='phones', parent=None, activity=True)
        cls.product_1 = Product.objects.create(name='test_product_1', category=cls.category, slug='t_prod_1')
        cls.product_2 = Product.objects.create(name='test_product_2', category=cls.category, slug='t_prod_2')
        seller = Seller.objects.create(name='test', profile=cls.profile, description='test')

        factory = RequestFactory()
        cls.request = factory.get('/order/step4/')
        cls.engine = import_module(settings.SESSION_ENGINE)
        cls.session_key = None
        cls.request.session = cls.engine.SessionStore(cls.session_key)
        cls.request.user = cls.user
        anonim_cart = AnonimCart(cls.request)

        for product in [cls.product_1, cls.product_2]:
            anonim_cart.add_product(product.id, 50)
            AuthShoppingCart.objects.create(user=cls.user, products=product, count=1, price=50)
            ProductImage.objects.create(product=product, image='/test_image/', image_alt='image.png')
            SellerProduct.objects.create(product=product, seller=seller, qty=1, price=10)

        cls.order_dict = {'full_name': 'test test test',
                          'phone': 1111111111,
                          'email': 'test mail',
                          'delivery': 'express',
                          'city': 'test city',
                          'address': 'test address',
                          'pay': 'test',
                          'added_date': date.today(),
                          'payment_status': 'Не оплачено'}

    def test_get_method_user_is_authenticate(self):
        cache.set('order', self.order_dict)
        self.client.login(username='test user', password='Asdfg54321')
        request = self.client.get(reverse('order_step_4'))

        self.assertEqual(request.context['t_price'], 600)
        self.assertEqual(len(request.context['products_list']), 2)
        self.assertEqual(request.context['order_dict'], self.order_dict)

    def test_post_method(self):
        self.client.login(username='test user', password='Asdfg54321')
        self.client.post(reverse('order_step_4'))
        order = OrderModel.objects.all().first()
        test_loaded_order_data = json.loads(order.json_order_data)
        self.order_dict['added_date'] = str(date.today())

        self.assertTrue(order)
        self.assertEqual(test_loaded_order_data['order_dict'], self.order_dict)
        self.assertTrue(order.activity)
        self.assertTrue(order.user)
