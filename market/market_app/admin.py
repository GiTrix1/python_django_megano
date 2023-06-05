from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin

from market_app.models import (
    ProductImage,
    ProductReview,
    ProductReviewImage,
    Product,
    SellerProduct,
    Seller,
    Discount,
    CharacteristicsGroup,
    Characteristic,
    CharacteristicValue,
)
from .models import Banner, Category


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    prepopulated_fields = {"slug": ("title",)}


@admin.register(CharacteristicsGroup)
class CharacteristicsGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'group_name']
    search_fields = ['group_name']


class CharacteristicValueInline(admin.TabularInline):
    model = CharacteristicValue


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    model = Characteristic
    list_display = ['id', 'characteristic_name', 'group']
    search_fields = ['characteristic_name', 'group']
    inlines = [CharacteristicValueInline, ]


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title1', 'price', 'image_alt', 'link']


class ProductImageInline(admin.TabularInline):
    """Класс для создания inline в модели товара в админке"""
    model = ProductImage
    extra = 1
    max_num = 7  # максимум 7 для корректного отображения на странице товара


class ProductReviewImageInline(admin.TabularInline):
    """Класс для создания inline в модели отзывов к товару в админке"""
    model = ProductReviewImage
    extra = 1
    max_num = 10


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Класс для работы с моделью товаров в админке"""
    list_display = ['id', 'name', 'category']
    list_filter = ['category']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]


@admin.register(SellerProduct)
class SellerProductAdmin(admin.ModelAdmin):
    """Класс для работы с моделью товаров у продавцов в админке"""
    list_display = ['id', 'product', 'seller', 'qty', 'price']
    list_filter = ['product', 'seller']
    search_fields = ['product', 'seller']


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    """Класс для работы с моделью продавцов в админке"""
    list_display = ['id', 'profile']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Класс для работы с моделью отзывов к товарам в админке"""
    list_display = ['product', 'customer', 'description_short']
    search_fields = ['product', 'customer']
    inlines = [ProductReviewImageInline]


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['discount']
