from market_app.models import Category


def get_categories(request):
    category_catalog = Category.objects.all()
    return {'categories': category_catalog}
