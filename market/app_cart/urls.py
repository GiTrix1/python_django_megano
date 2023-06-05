from django.urls import path
from .views import ShoppingCartView, AddToCartView, AddOneCountProductView, DelOneCountProductView, DelProductView

urlpatterns = [
    path('', ShoppingCartView.as_view(), name='cart'),
    path('add <int:product_id> <str:product_price>', AddToCartView.as_view(), name='add_cart'),
    path('add_one <int:product_id>', AddOneCountProductView.as_view(), name='add_one_cart'),
    path('del_one <int:product_id>', DelOneCountProductView.as_view(), name='del_one_cart'),
    path('del <int:product_id>', DelProductView.as_view(), name='del_product_cart'),
]
