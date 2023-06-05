from app_cart.models import AuthShoppingCart
from app_login.models import Profile


def delete_product_auth_user(request, product_id):

    """
    Функция для удаления одного продукта из корзины пользователя
    """

    current_product = AuthShoppingCart.objects.filter(user_id=request.user.id, products_id=product_id)
    current_product.delete()

    user = Profile.objects.filter(user_id=request.user.id)
    user_count = [count.product_in_cart for count in user.only('product_in_cart')]
    new_user_count = user_count[0] - 1
    user.update(
        product_in_cart=new_user_count
    )
