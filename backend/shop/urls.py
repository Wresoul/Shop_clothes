from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app_name = 'shop'


urlpatterns = [
    path('search/', views.search, name='search'),
    path('catalog/', views.catalog, name='catalog'),
    path('<slug:category_slug>/', views.catalog, name='index'),
    path('product/<slug:product_slug>/', views.product, name='product'),
]
