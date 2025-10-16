import json
import logging
from django.core.paginator import Paginator
from django.shortcuts import get_list_or_404, render
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import Categories, Goods
from .serializers import CategorySerializer, GoodsSerializer
from .utils import q_search
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.core.cache import cache
from django.http import JsonResponse
from broker.producer import send_to_kafka
from django.conf import settings


# Время жизни кэша (1 час)
TTL = 3600
logger = logging.getLogger(__name__)


def get_product_data(product_slug):
    product = Goods.objects.get(slug=product_slug)
    return {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'photo': product.photo.url if product.photo else None,
        'rating': product.rating,
        'discount': float(product.discount),
        'price': float(product.price),
        'quantity': product.quantity,
        'category': {
            'id': product.category.id,
            'name': product.category.name,
            'slug': product.category.slug
        },
        'display_id': product.display_id(),
        'sell_price': float(product.sell_price())
    }


def product(request, product_slug):
    try:
        product_data = get_product_data(product_slug)
        return render(request, "shop/product.html", context={'product': product_data})
    except ObjectDoesNotExist:
        return render(request, "shop/error.html", context={'error': 'Товар не найден'}, status=404)
    except Exception as e:
        return render(request, "shop/error.html", context={'error': str(e)}, status=500)



def cached_product(request, product_slug):
    key = f"product:{product_slug}"
    logger.debug(f"Checking cache for key: {key}", extra={'user': request.user.username if request.user.is_authenticated else 'anon', 'action': 'cache_check'})
    raw = cache.get(key)
    if raw is not None:
        logger.debug(f"Cache hit for {key}")
        product_data = json.loads(raw)
        return render(request, "shop/product.html", context={'product': product_data})

    logger.debug(f"Cache miss for {key}, querying database")
    try:
        message = {'event_type': 'product_view', 'slug': product_slug, 'cache_hit': bool(raw)}
        send_to_kafka(settings.KAFKA_TOPICS['logs'], message)
        product_data = get_product_data(product_slug)
        cache.set(key, json.dumps(product_data, cls=DjangoJSONEncoder), timeout=TTL)
        logger.debug(f"Cached data for {key}")
        return render(request, "shop/product.html", context={'product': product_data})
    except ObjectDoesNotExist:
        logger.error(f"Product not found: {product_slug}")
        return render(request, "shop/error.html", context={'error': 'Товар не найден'}, status=404)
    except Exception as e:
        logger.error(f"Error in cached_product: {str(e)}")
        return render(request, "shop/error.html", context={'error': str(e)}, status=500)

# Пагинация для API
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 100

# API ViewSets
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all().order_by('id')
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
