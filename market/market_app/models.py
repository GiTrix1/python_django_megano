from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import gettext_lazy as _


class Banner(models.Model):
    """ Модель рекламного баннера на главной странице сайта """
    title1 = models.CharField(max_length=50, verbose_name=_('заголовок 1'))
    title2 = models.CharField(max_length=100, blank=True, verbose_name=_('заголовок 2'))
    title3 = models.CharField(max_length=100, blank=True, verbose_name=_('заголовок 3'))
    text1 = models.CharField(max_length=100, blank=True, verbose_name=_('текст 1'))
    text_link = models.CharField(max_length=100, blank=True, verbose_name=_('текст кнопки со ссылкой'))
    price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2, verbose_name=_('цена'))
    image = models.ImageField(upload_to='images/banners', verbose_name=_('изображение'))
    image_alt = models.CharField(max_length=100, verbose_name=_('подсказка'))
    link = models.CharField(default='#', max_length=300, verbose_name='url')

    def __str__(self):
        return f"{self.id} - {self.title1}"

    class Meta:
        verbose_name = _('баннер')
        verbose_name_plural = _('баннеры')


class Seller(models.Model):
    """Модель продавца"""

    profile = models.ForeignKey("app_login.Profile", on_delete=models.CASCADE,
                                related_name='sellers', verbose_name=_('профиль')
                                )
    description = models.TextField(max_length=2000, blank=True, verbose_name=_('описание'))
    name = models.CharField(max_length=200, verbose_name=_('название магазина'))
    logo = models.ImageField(upload_to='seller_files/')

    class Meta:
        verbose_name = _('продавец')
        verbose_name_plural = _('продавцы')

    def __str__(self):
        return self.profile.user.username


class Category(MPTTModel):
    """
    Класс модели -> Category
    title - название категории;
    slug - повторение имени;
    parent - родительская категория;
    activity - флаг активности новости;
    """

    title = models.CharField(max_length=50, unique=True, verbose_name=_('Название'))
    image = models.FileField(verbose_name=_('Картинка категории товаров'), default=None, null=True, blank=True)
    image_big = models.FileField(verbose_name=_('Большая картинка категории товаров'), default=None, null=True,
                                 blank=True)
    image_alt = models.CharField(max_length=20, default=None, null=True, verbose_name=_('Название картинки категории'))
    slug = models.SlugField(verbose_name=_('Название ссылки'))
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children',
                            db_index=True, verbose_name=_('Родительская категория'))
    activity = models.BooleanField(default=False, blank=True, null=True, verbose_name=_('флаг активности'))

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        unique_together = [['parent', 'slug']]
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('catalog')


class Discount(models.Model):
    """Модель скидки для товаров"""
    discount = models.IntegerField()
    start_date = models.DateTimeField(verbose_name=_('дата начала'), default=timezone.now, blank=True, null=True)
    end_date = models.DateTimeField(verbose_name=_('Дата окончания'), blank=True, null=True)

    def __str__(self):
        return str(self.discount)

    class Meta:
        verbose_name = _('скидка')
        verbose_name_plural = _('скидки')


class Product(models.Model):
    """Модель товара"""
    name = models.CharField(max_length=255, db_index=True, verbose_name=_('название'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products',
                                 verbose_name=_('категория'))
    seller = models.ManyToManyField(Seller, through='SellerProduct', related_name='products',
                                    verbose_name=_('продавец'))
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL')
    description = models.TextField(max_length=2000, default='description', verbose_name=_('описание'))
    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('товар')
        verbose_name_plural = _('товары')


class CharacteristicsGroup(models.Model):
    group_name = models.CharField(max_length=30, verbose_name=_('название группы характеристик'))
    category = models.ManyToManyField(Category, verbose_name=_('категория'), related_name='characteristicsgroups')

    class Meta:
        verbose_name = _('группа характеристик')
        verbose_name_plural = _('группы характеристик')

    def __str__(self):
        return self.group_name


class Characteristic(models.Model):
    characteristic_name = models.CharField(max_length=30, verbose_name=_('название характеристики'))
    group = models.ForeignKey(CharacteristicsGroup, on_delete=models.CASCADE, verbose_name=_('группа характеристик'),
                              related_name='characteristics')

    class Meta:
        verbose_name = _('характеристика')
        verbose_name_plural = _('характеристики')

    def __str__(self):
        return self.characteristic_name


class CharacteristicValue(models.Model):
    value = models.CharField(max_length=200, verbose_name=_('значение характеристики'))
    characteristic = models.ForeignKey(Characteristic, verbose_name=_('характеристика'),
                                       on_delete=models.CASCADE, related_name='values')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True,
                                verbose_name=_('продукт'), related_name='values')

    class Meta:
        verbose_name = _('значение характеристик')
        verbose_name_plural = _('значения характеристик')

    def __str__(self):
        return f'{self.characteristic.characteristic_name} {self.product.name}'


class ProductImage(models.Model):
    """Модель фотографий к товарам"""
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name='images', verbose_name=_('товар'))
    image = models.ImageField(upload_to='images/products/%Y/%m/%d', verbose_name=_('картинка'))
    image_alt = models.CharField(max_length=100, default='Фото к товару', verbose_name=_('подсказка'))
    objects = models.Manager()


class SellerProduct(models.Model):
    """Промежуточная модель между моделями товара и продавца"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('товар'),
                                related_name='sellers_products')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name=_('продавец'),
                               related_name='sellers_products')
    qty = models.PositiveIntegerField(verbose_name=_('количество'))
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, verbose_name=_('скидка'), blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('цена'))
    objects = models.Manager()

    def __str__(self):
        return f'{self.product.name} - {self.seller.name}'

    class Meta:
        verbose_name = _('товар-продавец')
        verbose_name_plural = _('товар-продавец')


class HistoryView(models.Model):
    """ История просмотров пользователя """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('пользователь'), related_name='histories')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('товар'), related_name='histories')
    view_time = models.DateTimeField(auto_now=True, auto_created=True, verbose_name=_('время просмотра'))

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = _('история просмотров')
        verbose_name_plural = _('история просмотров')
        ordering = ['view_time']


class ProductReview(models.Model):
    """Модель отзывов к товарам определенных продавцов"""
    product = models.ForeignKey("Product", on_delete=models.CASCADE, verbose_name=_('товар'),
                                related_name='reviews'
                                )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('покупатель'), related_name='reviews')
    description = models.TextField(max_length=2000, verbose_name=_('описание'))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('дата'))

    def description_short(self):
        """
        Функция возвращает описание, если его длина меньше 15 символов, иначе возвращает
        срез первых 15 символов с многоточием.
        :return: обрезанное описание.
        """
        if len(self.description) > 15:
            return self.description[:15] + '...'
        return self.description

    def __str__(self):
        return f'Запись: {self.description_short()}, Пользователь: {self.customer}'

    class Meta:
        verbose_name = _('отзыв')
        verbose_name_plural = _('отзывы')


class ProductReviewImage(models.Model):
    """Модель фотографий к отзывам"""
    review = models.ForeignKey("ProductReview", on_delete=models.CASCADE, related_name='images',
                               verbose_name=_('отзыв'))
    image = models.ImageField(upload_to='images/product_reviews/%Y/%m/%d', verbose_name=_('картинка'))
    image_alt = models.CharField(max_length=100, default='Фото к отзыву', verbose_name=_('подсказка'))


class ProductPurchases(models.Model):
    """
    Модель товаров к кол-ву раз, сколько их покупали
    """

    product = models.OneToOneField(Product, on_delete=models.CASCADE, unique=True, verbose_name='продукт')
    num_purchases = models.PositiveIntegerField(verbose_name='кол-во покупок с данным товаром')

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = 'товар-покупки'
        verbose_name_plural = 'товары-покупки'
