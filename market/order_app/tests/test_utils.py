from django.core.cache import cache
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from django.utils.module_loading import import_module

from order_app.models import OrderModel
from order_app.utils import add_data_in_order_cache, delete_data_from_order_cache, is_one_seller, \
    get_data_from_cart_for_auth_user, calculate_delivery_cost, create_order_object
from app_login.models import Profile
from market_app.models import Product, Seller, SellerProduct, Category, ProductImage
from app_cart.models import AuthShoppingCart


class AddDataInOrderCacheFuncTest(TestCase):
    TEST_1 = 'test test test'
    TEST_2 = '0000000000'
    TEST_3 = 'test@mail.ru'

    def test_ordinary_situation(self):
        data_dict = {'test_1': self.TEST_1,
                     'test_2': self.TEST_2,
                     'test_3': self.TEST_3}
        add_data_in_order_cache(**data_dict)
        order_dict = cache.get('order')

        self.assertIsNotNone(order_dict)
        self.assertEqual(order_dict['test_3'], 'test@mail.ru')


class DeleteDataFromOrderCacheFuncTest(TestCase):

    def test_ordinary_situation(self):
        data_dict = {'test_1': 'test', 'test_2': 'test', 'test_3': 'test'}
        cache.set('order', data_dict)
        delete_data_from_order_cache(*data_dict.keys())
        order_dict = cache.get('order')
        cache.clear()

        self.assertNotIn('test_2', order_dict.keys())


class IsOneSeller(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='test user', password='Asdfg54321')
        profile = Profile.objects.create(user=user, full_name='test test test', phone='888888')
        category = Category.objects.create(title='телефоны', slug='phones', parent=None, activity=True)
        cls.product_1 = Product.objects.create(name='test_product_1', category=category, slug='t_prod_1')
        cls.product_2 = Product.objects.create(name='test_product_2', category=category, slug='t_prod_2')
        cls.product_3 = Product.objects.create(name='test_product_3', category=category, slug='t_prod_3')
        seller_1 = Seller.objects.create(name='test seller 1', profile=profile, description='test')
        seller_2 = Seller.objects.create(name='test seller 2', profile=profile, description='test')
        SellerProduct.objects.create(product=cls.product_1, seller=seller_1, qty=1, price=10)
        SellerProduct.objects.create(product=cls.product_2, seller=seller_1, qty=1, price=10)
        SellerProduct.objects.create(product=cls.product_3, seller=seller_2, qty=1, price=10)

    def test_one_seller(self):
        products_id = [product.id for product in [self.product_1, self.product_2]]
        result = is_one_seller(products_id)

        self.assertTrue(result)

    def test_few_sellers(self):
        products_id = [product.id for product in [self.product_1, self.product_2, self.product_3]]
        result = is_one_seller(products_id)

        self.assertFalse(result)


class GetDataFromCartForAuthUserFuncTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='test user', password='Asdfg54321')
        profile = Profile.objects.create(user=user, full_name='test test test', phone='888888')
        category = Category.objects.create(title='телефоны', slug='phones', parent=None, activity=True)
        cls.product_1 = Product.objects.create(name='test_product_1', category=category, slug='t_prod_1')
        cls.product_2 = Product.objects.create(name='test_product_2', category=category, slug='t_prod_2')
        cls.product_3 = Product.objects.create(name='test_product_3', category=category, slug='t_prod_3')
        seller = Seller.objects.create(name='test seller 1', profile=profile, description='test')
        for product in [cls.product_1, cls.product_2, cls.product_3]:
            AuthShoppingCart.objects.create(user=user, products=product, count=1, price=50)
            ProductImage.objects.create(product=product, image='/test_image/', image_alt='image.png')
            SellerProduct.objects.create(product=product, seller=seller, qty=1, price=10)

        cls.factory = RequestFactory()
        cls.request = cls.factory.get('/order/')
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        cls.request.session = engine.SessionStore(session_key)
        cls.request.user = user

    def test_ordinary_situation(self):
        total_price, products, one_seller = get_data_from_cart_for_auth_user(self.request)

        self.assertEqual(total_price, 150)
        self.assertEqual(len(products), 3)
        self.assertTrue(one_seller)


class CalculateDeliveryCostFuncTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.order_data = {'t_price': 1999, 'products_list': None, 'order_dict': {'delivery': 'ordinary'}}

    def test_express_delivery(self):
        self.order_data['order_dict']['delivery'] = 'express'
        del_cost = calculate_delivery_cost(self.order_data, True)

        self.assertEqual(del_cost, 500)

    def test_ordinary_delivery_amount_less_than_2000(self):
        del_cost = calculate_delivery_cost(self.order_data, True)

        self.assertEqual(del_cost, 200)

    def test_ordinary_delivery_amount_more_than_2000(self):
        self.order_data['t_price'] = 2001
        del_cost = calculate_delivery_cost(self.order_data, True)

        self.assertEqual(del_cost, 0)

    def test_few_sellers(self):
        del_cost = calculate_delivery_cost(self.order_data, False)

        self.assertEqual(del_cost, 200)


class CheckCacheFuncTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='test user', password='Asdfg54321')

    def setUp(self) -> None:
        self.client.login(username='test user', password='Asdfg54321')

    def test_cache_order_is_empty(self):
        cache.clear()
        request = self.client.get(reverse('order_step_4'))

        self.assertRedirects(request, reverse('order_step_1'))

    def test_cache_order_only_with_delivery(self):
        order_dict_with_delivery = {'delivery': 'express',
                                    'city': 'test',
                                    'address': 'test address'}
        cache.set('order', order_dict_with_delivery)
        request = self.client.get(reverse('order_step_4'))

        self.assertRedirects(request, reverse('order_step_1'))

    def test_cache_only_with_payment_method(self):
        order_dict_with_payment_method = {'pay': 'someone'}
        cache.set('order', order_dict_with_payment_method)
        request = self.client.get(reverse('order_step_4'))

        self.assertRedirects(request, reverse('order_step_1'))


class CreateOrderObjectFuncTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test user', password='Asdfg54321')
        cls.order_data = {'test': 'test', 'products': [{'test': 'test'}, {'test_2': 'test'}], 'o': {'test': 'test'}}

    def test_ordinary_situation(self):
        create_order_object(self.user, self.order_data)
        created_object = OrderModel.objects.filter(user=self.user)

        self.assertTrue(created_object)
        self.assertTrue(created_object.first().json_order_data)
