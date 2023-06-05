from app_cart.models import AnonimCart, AuthShoppingCart


def get_products_in_cart(request):
    if request.user.is_authenticated:
        num_products = len(AuthShoppingCart.objects.filter(user=request.user))

    else:
        anonim_cart_obj = AnonimCart(request=request)
        num_products = anonim_cart_obj.get_count_product_in_cart()

    return {'num_products_in_cart': num_products}
