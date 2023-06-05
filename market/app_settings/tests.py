from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import SiteSettings


class TestSettingsView(TestCase):
    """Класс тестов страницы настроек сайта"""
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', password='testpassword')
        self.user = User.objects.create_user(username='user', password='testpassword')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.superuser)

    def test_settings_exist(self):
        """Проверка существования записи с настройками"""
        settings = SiteSettings.objects.exists()
        self.assertTrue(settings)

    def test_settings_exist_at_desired_location_for_superuser(self):
        """Проверка открытия страницы для superuser"""
        response = self.authorized_client.get('/settings/')
        self.assertEqual(response.status_code, 200)

    def test_settings_do_not_exist_for_simple_user(self):
        """Проверка перенаправления для обычного пользователя"""
        self.client.login(username='user', password='testpassword')
        response = self.client.get('/settings/')
        self.assertEqual(response.status_code, 302)

    def test_account_edit_uses_correct_template(self):
        """Проверка использования корректного шаблона"""
        response = self.authorized_client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_settings/settings.html')

    def test_setting_edit(self):
        """Проверка работоспособности изменения настроек из формы на странице"""
        form_data = {"site_name": "new_name",
                     "phone_number1": "new_phone1",
                     "phone_number2": "new_phone2",
                     "address": "new_address",
                     "banner_number": 2,
                     "stopping_sales": True,
                     "banner_cache_time": 100,
                     "total_cache_time": 200,
                     "seller_cache_time": 300,
                     "sellers_products_top_cache_time": 400,
                     "sellers_products_top_number": 10,
                     "common_products_top_number": 10,
                     "ordinary_delivery_cost": 200,
                     "min_amount_for_free_delivery": 2000,
                     "express_delivery_cost": 500,
                     "num_reviews_per_page": 3,
                     "num_products_per_page": 4,
                     }
        response = self.authorized_client.post(reverse('settings'), form_data)
        self.assertRedirects(response, reverse('settings'))

        settings = SiteSettings.objects.first()
        self.assertEqual(settings.site_name, "new_name")
        self.assertEqual(settings.phone_number1, "new_phone1")
        self.assertEqual(settings.phone_number2, "new_phone2")
        self.assertEqual(settings.address, "new_address")
        self.assertEqual(settings.banner_number, 2)
        self.assertEqual(settings.stopping_sales, True)
        self.assertEqual(settings.banner_cache_time, 100)
        self.assertEqual(settings.total_cache_time, 200)
        self.assertEqual(settings.seller_cache_time, 300)
        self.assertEqual(settings.sellers_products_top_cache_time, 400)
        self.assertEqual(settings.sellers_products_top_number, 10)
        self.assertEqual(settings.common_products_top_number, 10)
        self.assertEqual(settings.ordinary_delivery_cost, 200)
        self.assertEqual(settings.min_amount_for_free_delivery, 2000)
        self.assertEqual(settings.express_delivery_cost, 500)
        self.assertEqual(settings.num_reviews_per_page, 3)
        self.assertEqual(settings.num_products_per_page, 4)
