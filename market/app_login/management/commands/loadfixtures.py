from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Загрузка всех фикстур'

    def handle(self, *args, **options):
        management.call_command('loaddata', 'app_login/fixtures/users.json')
        management.call_command('loaddata', 'app_login/fixtures/avatarprofiles.json')
        management.call_command('loaddata', 'app_login/fixtures/profiles.json')
        management.call_command('loaddata', 'api_for_payment_app/card_model.json')
        management.call_command('loaddata', 'api_for_payment_app/paymentstatusmodel.json')
        management.call_command('loaddata', 'market_app/fixtures/banners.json')
        management.call_command('loaddata', 'market_app/fixtures/categories.json')
        management.call_command('loaddata', 'market_app/fixtures/sellers.json')
        management.call_command('loaddata', 'market_app/fixtures/products.json')
        management.call_command('loaddata', 'market_app/fixtures/product_images.json')
        management.call_command('loaddata', 'market_app/fixtures/seller_products.json')
        management.call_command('loaddata', 'market_app/fixtures/product_reviews.json')
        management.call_command('loaddata', 'market_app/fixtures/characteristicsgroups.json')
        management.call_command('loaddata', 'market_app/fixtures/characteristics.json')
        management.call_command('loaddata', 'market_app/fixtures/characteristicvalues.json')
        management.call_command('loaddata', 'order_app/fixtures/order_model.json')
