from decimal import Decimal
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from app_login.models import Profile
from market_app.models import ProductImage, Product
from .models import AuthShoppingCart, AnonimCart
from market_app.utils import get_count_product_in_cart
from app_cart.utils import delete_product_auth_user


class ShoppingCartView(View):

    def get(self, request):

        shopping_cart = list()
        total = None
        count_in_cart = get_count_product_in_cart(request)

        if request.user.is_authenticated:

            cart = AuthShoppingCart.objects.filter(user_id=request.user.id).select_related('products').all()

            if len(cart) != 0:
                total = sum([item.price*item.count for item in cart])

                for cart_item in cart:

                    item_image = [obj for obj in ProductImage.objects.filter(product_id=cart_item.products.id)]
                    shopping_carts = {
                        'id': cart_item.products.id,
                        'name': cart_item.products.name,
                        'description': f'{cart_item.products.description[:90]}...',
                        'image': item_image[0].image,
                        'image_alt': item_image[0].image_alt,
                        'price': cart_item.price,
                        'count': cart_item.count
                    }
                    shopping_cart.append(shopping_carts)

        else:

            cart = AnonimCart(request)
            total = cart.get_total_price()
            anonim_cart = cart.get_cart()

            for cart_item in anonim_cart.keys():

                products = [cart_product for cart_product in Product.objects.filter(id=int(cart_item))]
                product_price = Decimal(anonim_cart[cart_item]['price'])
                item_image = [cart_item_image for cart_item_image in ProductImage.objects.filter(
                    product_id=int(cart_item))]
                shopping_carts = {
                    'id': products[0].id,
                    'name': products[0].name,
                    'description': f'{products[0].description[:90]}...',
                    'image': item_image[0].image,
                    'image_alt': item_image[0].image_alt,
                    'price': product_price,
                    'count': anonim_cart[cart_item]['count']
                }
                shopping_cart.append(shopping_carts)

        return render(request, 'cart.html', {'context': shopping_cart,
                                             'total_price': total,
                                             'product_in_cart': count_in_cart})


class AddToCartView(View):

    def get(self, request, product_id, product_price):

        if request.user.is_authenticated:

            current_product = AuthShoppingCart.objects.filter(user_id=request.user.id, products_id=product_id)

            if len(current_product) == 0:

                product_price = Decimal(product_price)

                AuthShoppingCart.objects.create(
                    user_id=request.user.id,
                    products_id=product_id,
                    count=1,
                    price=product_price
                )
                user = Profile.objects.filter(user_id=request.user.id)
                user_count = [count.product_in_cart for count in user.only('product_in_cart')]
                new_user_count = user_count[0] + 1
                user.update(
                    product_in_cart=new_user_count
                )

        else:

            cart = AnonimCart(request)
            cart.add_product(product_id, product_price)

        return HttpResponseRedirect(f'/product/{product_id}')


class AddOneCountProductView(View):

    def get(self, request, product_id):

        if request.user.is_authenticated:

            current_product = AuthShoppingCart.objects.filter(user_id=request.user.id, products_id=product_id)
            current_product_count = [product_count.count for product_count in current_product.only('count')]
            current_product.update(
                count=current_product_count[0] + 1
            )

        else:

            cart = AnonimCart(request)
            cart.add_one(product_id)

        return HttpResponseRedirect('/cart')


class DelOneCountProductView(View):

    def get(self, request, product_id):

        if request.user.is_authenticated:

            current_product = AuthShoppingCart.objects.filter(user_id=request.user.id, products_id=product_id)
            current_product_count = [product_count.count for product_count in current_product.only('count')]
            new_product_count = current_product_count[0] - 1

            if new_product_count <= 0:

                current_product.update(
                    count=current_product_count[0]
                )

            else:

                current_product.update(
                    count=new_product_count
                )

        else:

            cart = AnonimCart(request)
            cart.remove_one(product_id)

        return HttpResponseRedirect('/cart')


class DelProductView(View):

    def get(self, request, product_id):

        if request.user.is_authenticated:

            delete_product_auth_user(request, product_id)

        else:

            cart = AnonimCart(request)
            cart.remove_product(product_id)

        return HttpResponseRedirect('/cart')
