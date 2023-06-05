from django.test import TestCase
from django.core.cache import cache

from market_app.models import Product, CharacteristicsGroup, Characteristic, CharacteristicValue, ProductImage,\
    Category
from ..views import get_products_for_compare


class AddGoodForCompareTestClass(TestCase):
    category_name_1 = 'test_category_1'
    category_name_2 = 'test_category_2'
    product_name = 'test product'

    @classmethod
    def setUpClass(cls):
        super(AddGoodForCompareTestClass, cls).setUpClass()
        category = Category.objects.create(title=cls.category_name_1)
        another_category = Category.objects.create(title=cls.category_name_2)
        Product.objects.create(name=cls.product_name, category=category, slug='abc')
        Product.objects.create(name=cls.product_name, category=another_category, slug='def')

    def test_ordinary_situation(self):
        """
        Проверка на то, что товар добавляется в кэш
        """
        self.client.get(f'/comparison/add/{1}/')
        compare_object = cache.get('compare_object')
        cache.clear()

        self.assertTrue(compare_object)
        self.assertEqual(compare_object['products_list'][0], 1)

    def test_another_category(self):
        """
        Тестирование функционала, не допускающего добавление для сравнения товаров из разных категорий
        """
        self.client.get(f'/comparison/add/{1}/')
        resp = self.client.get(f'/comparison/add/{2}/')
        compare_object = cache.get('compare_object')
        cache.clear()

        self.assertEqual(resp.context['isFalseCategory'], True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(compare_object['products_list']), 1)

    def test_more_than_two_items(self):
        """
        Тестирование функционала, не допускающего добавление для сравнения более 2-ух товаров
        """
        for _ in range(3):
            self.client.get(f'/comparison/add/{1}/')
        compare_object = cache.get('compare_object')
        cache.clear()

        self.assertEqual(len(compare_object['products_list']), 2)


class RemoveGoodForCompareTestClass(TestCase):
    category_name = 'test category'
    product_name = 'test product'

    @classmethod
    def setUpClass(cls):
        super(RemoveGoodForCompareTestClass, cls).setUpClass()
        category = Category.objects.create(title=cls.category_name)
        cls.product_1 = Product.objects.create(name=cls.product_name, category=category, slug='ghi')
        cls.product_2 = Product.objects.create(name=cls.product_name, category=category, slug='klm')
        cache.set('compare_object', {
            'category_for_compare': category,
            'products_list': [cls.product_1.id, cls.product_2.id]
        })

    def test_ordinary_situation(self):
        """
        Проверка на то, что нужный товар удаляется из кэша
        """
        resp = self.client.get(f'/comparison/remove/{self.product_2.id}/')
        compare_object = cache.get('compare_object')

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(compare_object['products_list']), 1)

    def test_zero_items(self):
        """
        Проверка на то, что при удалении последнего товара из кэша, оттуда же удаляется сама структура 'compare_object'
        """
        resp = self.client.get(f'/comparison/remove/{self.product_1.id}/')
        compare_object = cache.get('compare_object')
        cache.clear()

        self.assertEqual(resp.status_code, 302)
        self.assertFalse(compare_object)


class GetProductsForCompareFuncTestClass(TestCase):
    category_name = 'test'
    product_name = 'test product 1'
    group_name_1 = 'test_group_1'
    group_name_2 = 'test_group_2'
    characteristic_name_1 = 'characteristic_name_1'
    characteristic_name_2 = 'characteristic_name_2'
    characteristic_name_3 = 'characteristic_name_3'
    characteristic_name_4 = 'characteristic_name_4'

    @classmethod
    def setUpClass(cls):
        super(GetProductsForCompareFuncTestClass, cls).setUpClass()
        category = Category.objects.create(title=cls.category_name)
        cls.product = Product.objects.create(name=cls.product_name, category=category, slug='lmn')
        cls.image = ProductImage.objects.create(product=cls.product, image='/test/test/test')
        cls.group_1 = CharacteristicsGroup.objects.create(group_name=cls.group_name_1)
        cls.group_1.category.add(category)
        cls.group_2 = CharacteristicsGroup.objects.create(group_name=cls.group_name_2)
        cls.group_2.category.add(category)
        cls.char_1 = Characteristic.objects.create(characteristic_name=cls.characteristic_name_1, group=cls.group_1)
        cls.char_2 = Characteristic.objects.create(characteristic_name=cls.characteristic_name_2, group=cls.group_1)
        cls.char_3 = Characteristic.objects.create(characteristic_name=cls.characteristic_name_3, group=cls.group_2)
        cls.char_4 = Characteristic.objects.create(characteristic_name=cls.characteristic_name_4, group=cls.group_2)
        cls.value_1 = CharacteristicValue.objects.create(value='test', characteristic=cls.char_1, product=cls.product)
        cls.value_2 = CharacteristicValue.objects.create(value='test', characteristic=cls.char_2, product=cls.product)
        cls.value_3 = CharacteristicValue.objects.create(value='test', characteristic=cls.char_3, product=cls.product)
        cls.value_4 = CharacteristicValue.objects.create(value='test', characteristic=cls.char_4, product=cls.product)
        cache.set('compare_objects', {
            'category_for_compare': category,
            'products_list': [cls.product.id]
        })

    def test_ordinary_situation(self):
        """
        Проверка поведения функции и возвращаемых ею данных при запланированном сценарии
        """
        compare_object = cache.get('compare_objects')
        products_dict = get_products_for_compare(compare_object=compare_object)
        product_data_dict = products_dict[self.product_name]
        characteristics_groups_dict = product_data_dict['characteristics']

        # Такое большое кол-во проверок необходимо ввиду особой важности формируемых функцией данных
        self.assertEqual(len(products_dict.keys()), 1)
        self.assertEqual(list(products_dict.keys())[0], self.product.name)

        # Проверка корректности пути к картинке товара и его id
        self.assertEqual(product_data_dict['image_path'], self.image.image)
        self.assertEqual(product_data_dict['product_id'], self.product.id)

        # Проверка кол-ва сформированных групп характеристик и корректности их названий
        self.assertEqual(len(characteristics_groups_dict), 2)
        self.assertEqual(list(characteristics_groups_dict.keys())[0], self.group_1.group_name)
        self.assertEqual(list(characteristics_groups_dict.keys())[1], self.group_2.group_name)

        # Проверка кол-ва сформированных списков с конкретными характеристиками в каждой группе
        self.assertEqual(len(characteristics_groups_dict[self.group_1.group_name]), 2)
        self.assertEqual(len(characteristics_groups_dict[self.group_2.group_name]), 2)

        # Проверка того, что в каждом списке с характеристикой присутствует 2 элемента (ее название и значение)
        self.assertEqual(len(characteristics_groups_dict[self.group_1.group_name][0]), 2)
        self.assertEqual(len(characteristics_groups_dict[self.group_1.group_name][1]), 2)
        self.assertEqual(len(characteristics_groups_dict[self.group_2.group_name][0]), 2)
        self.assertEqual(len(characteristics_groups_dict[self.group_2.group_name][1]), 2)

        # Проверка корректности названий характеристик и их значений
        self.assertEqual(characteristics_groups_dict[self.group_1.group_name][0][0], self.char_1.characteristic_name)
        self.assertEqual(characteristics_groups_dict[self.group_1.group_name][0][1], self.value_1.value)
        self.assertEqual(characteristics_groups_dict[self.group_1.group_name][1][0], self.char_2.characteristic_name)
        self.assertEqual(characteristics_groups_dict[self.group_1.group_name][1][1], self.value_2.value)
        self.assertEqual(characteristics_groups_dict[self.group_2.group_name][0][0], self.char_3.characteristic_name)
        self.assertEqual(characteristics_groups_dict[self.group_2.group_name][0][1], self.value_3.value)
        self.assertEqual(characteristics_groups_dict[self.group_2.group_name][1][0], self.char_4.characteristic_name)
        self.assertEqual(characteristics_groups_dict[self.group_2.group_name][1][1], self.value_4.value)
