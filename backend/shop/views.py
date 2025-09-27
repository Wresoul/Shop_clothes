from django.core.paginator import Paginator
from django.shortcuts import get_list_or_404, render
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import Categories, Goods
from .serializers import CategorySerializer, GoodsSerializer
from .utils import q_search

# Пагинация для API
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 100

# API ViewSets
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class GoodsViewSet(viewsets.ModelViewSet):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['price', 'rating', 'name']
    search_fields = ['name', 'description']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category_slug', None)
        on_sale = self.request.query_params.get('on_sale', None)
        query = self.request.query_params.get('q', None)

        if category_slug and category_slug != 'all':
            queryset = queryset.filter(category__slug=category_slug)
        if on_sale:
            queryset = queryset.filter(discount__gt=0)
        if query:
            queryset = q_search(query)

        return queryset

# HTML Views (оставляем ваши текущие представления)
def search(request, category_slug=None):
    goods = Goods.objects.all()
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
        "goods": current_page
    }
    return render(request, "shop/shop.html", context)

def catalog(request, category_slug=None):
    goods = Goods.objects.all()
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
        "goods": current_page
    }
    return render(request, "shop/shop.html", context)

def product(request, product_slug):
    product = Goods.objects.get(slug=product_slug)
    context = {"product": product}
    return render(request, "shop/product.html", context=context)