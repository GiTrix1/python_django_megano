from decimal import Decimal
from app_cart.models import AnonimCart, AuthShoppingCart


def transfer_to_auth_cart(request, user):
    anonim_cart = AnonimCart(request)
    if len(anonim_cart.get_cart()) != 0:
        cart = anonim_cart.get_cart()
        for item in cart.keys():
            product = int(item)
            AuthShoppingCart.objects.create(
                user_id=user.id,
                products_id=product,
                count=cart[item]['count'],
                price=Decimal(cart[item]['price'])
            )
        cart.clear()
