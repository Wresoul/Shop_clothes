"""
URL configuration for DjangoProject2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from shop.views import GoodsViewSet, CategoryViewSet
from carts.views import CartViewSet
from orders.views import OrderViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'goods', GoodsViewSet, basename='goods')
router.register(r'shop-categories', CategoryViewSet, basename='category')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'carts', CartViewSet, basename='cart')
# Уникальный префикс

urlpatterns = [
       path('admin/', admin.site.urls),
       path('', include('main.urls', namespace='main')),
       path('shop/', include('shop.urls', namespace='shop')),
       path('users/', include('users.urls', namespace='users')),
       path('orders/', include('orders.urls', namespace='orders')),
       path('carts/', include('carts.urls', namespace='carts')),
       path('api/', include(router.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
