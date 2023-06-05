from decimal import Decimal
from django.contrib.auth.models import User
from market_app.models import Product
from django.db import models
from django.utils.translation import gettext_lazy as _


class AnonimCart(object):

    """
    Сессионная корзина анонимного пользователя
    """

    def __init__(self, request):

        """
        Иннициализация сессионной корзины
        """

        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True

    def add_product(self, product_id, price):
        product_id = str(product_id)
        if product_id not in self.cart:
            self.cart[product_id] = {'count': 1,
                                     'price': price}
        self.save()

    def add_one(self, product_id):
        product_id = str(product_id)
        self.cart[product_id]['count'] += 1
        self.save()

    def remove_one(self, product_id):
        product_id = str(product_id)
        count = self.cart[product_id]['count']
        new_count = count - 1
        if new_count <= 0:
            self.cart[product_id]['count'] = count
        else:
            self.cart[product_id]['count'] = new_count
        self.save()

    def remove_product(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_cart(self):
        return self.cart

    def get_count_product_in_cart(self):
        return sum(int(product) for product in self.cart.keys())

    def get_total_price(self):
        return sum(Decimal(item['price'])*item['count'] for item in self.cart.values())

    def clear(self):
        del self.session['cart']
        self.session.modified = True


class AuthShoppingCart(models.Model):

    """
    Модель пользовательской корзины
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        verbose_name='User cart'
    )
    products = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name='Товары',
        verbose_name='Товары в корзине'
    )
    item_added = models.DateTimeField(
        auto_now_add=True
    )
    count = models.IntegerField(
        default=0,
        verbose_name='Количество товаров в корзине'
    )
    price = models.DecimalField(
        default=None,
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за товар'
    )
    objects = models.Manager()

    class Meta:
        verbose_name_plural = _('Покупательские корзины')
        verbose_name = _('Покупательская корзина')
        ordering = ['item_added']
