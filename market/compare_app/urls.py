from django.urls import path
from .views import get_products_list_for_compare_view, add_product_for_compare_view, remove_good_for_compare_view


urlpatterns = [
    path('', get_products_list_for_compare_view, name='compare-goods'),
    path('add/<int:product_id>/', add_product_for_compare_view, name='add-good-for-compare'),
    path('remove/<int:product_id>/', remove_good_for_compare_view, name='remove good for compare'),
]
