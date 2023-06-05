import json

from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from django.contrib.auth.models import User

from order_app.models import OrderModel
from app_login.models import Profile


class OrderTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cache.set('order', {'full_name': 'test', 'delivery': 'express', 'city': 'test', 'address': 'test',
                            'phone': 'test', 'mail': 'test', 'pay': 'test'})
        user = User.objects.create_user(username='test user')
        user.set_password('Asdfg54321')
        user.save()
        Profile.objects.create(user=user, full_name='test test test', phone='888888')
        json_order_data = json.dumps({'test': 'test', 'products': [{'test': 'test'}, {'test_2': 'test'}],
                                      'order_dict': {'pay': 'online'}})
        cls.order_object = OrderModel.objects.create(user=user, json_order_data=json_order_data)

    def test_correct_template_in_order(self):
        self.client.login(username='test user', password='Asdfg54321')
        step_1 = self.client.get(reverse('order_step_1'))
        step_2 = self.client.get(reverse('order_step_2'))
        step_3 = self.client.get(reverse('order_step_3'))
        step_4 = self.client.get(reverse('order_step_4'))
        order_detail = self.client.get(reverse('order_detail', kwargs={'order_id': self.order_object.id}))
        cache.clear()
        self.order_object.delete()

        self.assertTemplateUsed(step_1, 'order/order_step_1.html')
        self.assertTemplateUsed(step_2, 'order/order_step_2.html')
        self.assertTemplateUsed(step_3, 'order/order_step_3.html')
        self.assertTemplateUsed(step_4, 'order/order_step_4.html')
        self.assertTemplateUsed(order_detail, 'order/oneorder.html')
