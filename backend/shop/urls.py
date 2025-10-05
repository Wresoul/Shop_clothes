from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.views.decorators.cache import cache_page


app_name = 'shop'


urlpatterns = [
    path('search/', views.search, name='search'),
    path('catalog/', cache_page(60*5)(views.catalog), name='catalog'),
    path('<slug:category_slug>/', views.catalog, name='index'),
    path('product/<slug:product_slug>/', views.cached_product, name='product'),
]
