from django.core.paginator import Paginator
from django.shortcuts import get_list_or_404, render

from shop.models import Goods
from shop.utils import q_search
# Create your views here.

def search(request, category_slug=None):
    goods= Goods.objects.all()
    page = request.GET.get('page', 1)
    on_sale = request.GET.get('on_sale', None)
    order_by = request.GET.get('order_by', None)
    query = request.GET.get('q', None)

    if category_slug == "all":
        goods = Goods.objects.all()
    elif query:
        goods = q_search(query)
    else:
        goods = get_list_or_404(Goods.objects.filter(category__slug=category_slug))

    if on_sale:
        goods = goods.filter(discount__gt=0)

    if order_by and order_by != "default":
        goods = goods.order_by(order_by)

    paginator = Paginator(goods, 3)

    current_page = paginator.page(int(page))


    context = {
        "title": "Home - Каталог",
        "slug_url": category_slug,
        "goods" : current_page
    }

    return render(request, "shop/shop.html", context, )


def catalog(request, category_slug=None):
    goods= Goods.objects.all()
    page = request.GET.get('page', 1)
    on_sale = request.GET.get('on_sale', None)
    order_by = request.GET.get('order_by', None)
    query = request.GET.get('q', None)


    if on_sale:
        goods = goods.filter(discount__gt=0)

    if order_by and order_by != "default":
        goods = goods.order_by(order_by)

    paginator = Paginator(goods, 3)

    current_page = paginator.page(int(page))


    context = {
        "title": "Home - Каталог",
        "slug_url": category_slug,
        "goods" : current_page
    }

    return render(request, "shop/shop.html", context, )


def product(request, product_slug):
    product = Goods.objects.get(slug=product_slug)

    context = {"product": product}

    return render(request, "shop/product.html", context=context)
