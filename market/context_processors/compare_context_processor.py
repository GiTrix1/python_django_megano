from django.core.cache import cache


def get_amount_products_for_compare(request):
    compare_object = cache.get('compare_object')
    if not compare_object:
        amount = 0
    else:
        amount = len(compare_object['products_list'])
    return {'amount_products_for_compare': amount}
