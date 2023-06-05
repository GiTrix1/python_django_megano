import time

from django.contrib.auth.models import User
from django.test import TestCase

from market_app.product_history import HistoryViewOperations
from market_app.models import Category, HistoryView, Product


class HistoryViewOperationsTest(TestCase):
    """ Тест методов класса HistoryViewOperations """

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('test_user')
        cls.user = user
        category = Category.objects.create()
        cls.products = list()
        for num in range(1, 22):
            slug = 'a' * num
            product = Product.objects.create(name=f'Product {num}', category=category, slug=slug)
            cls.products.append(product)
        cls.history = HistoryViewOperations(user=user)

    def test_add_product(self):
        """ Тест добавления одного товара """
        product = self.products[0]
        self.history.add_product(product)
        count = HistoryView.objects.filter(user=self.user).count()
        self.assertEqual(count, 1)

    def test_get_product_list(self):
        """ Тест получения списка товаров """
        self.history.add_product(self.products[0])
        self.history.add_product(self.products[1])
        product_list = list(self.history.products())
        self.assertEqual(product_list, [self.products[1], self.products[0]])

    def test_product_delete(self):
        """ Тест удаления товара из истории просмотров """
        products = self.products[:10]
        for product in products:
            self.history.add_product(product)
        products.reverse()
        self.history.delete_product(products[5])
        products.pop(5)
        product_list_from_history = list(self.history.products())
        self.assertEqual(products, product_list_from_history)

    def test_count(self):
        """ Тест получения количества продуктов в истории """
        for product in self.products[:10]:
            self.history.add_product(product)

        self.assertEqual(self.history.count(), 10)

    def test_different_user_history(self):
        """ Тест добавления и получения списка товаров для разных пользователей """
        user2 = User.objects.create_user(username='test_user_2')
        history2 = HistoryViewOperations(user2)
        user3 = User.objects.create_user(username='test_user_3')
        history3 = HistoryViewOperations(user3)

        history2.add_product(self.products[0])
        history3.add_product(self.products[1])

        self.assertEqual(list(history2.products()), [self.products[0]])
        self.assertEqual(list(history3.products()), [self.products[1]])

    def test_order(self):
        """ Тест изменения порядка товаров при повторном добавлении товара """
        self.history.add_product(self.products[0])
        time.sleep(0.1)
        self.history.add_product(self.products[1])
        time.sleep(0.1)
        self.history.add_product(self.products[0])

        products_list = [self.products[0], self.products[1]]
        self.assertEqual(list(self.history.products()), products_list)

    def test_add_21(self):
        """ Тест добавления 21-го товара """
        for product in self.products:
            self.history.add_product(product)

        result_product_list = self.products[1:]
        product_history_list = list(self.history.products())
        product_history_list.reverse()

        self.assertEqual(result_product_list, product_history_list)
