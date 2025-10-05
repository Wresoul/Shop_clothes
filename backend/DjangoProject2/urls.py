from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from shop.views import GoodsViewSet, CategoryViewSet
from carts.views import CartViewSet
from orders.views import OrderViewSet
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Shop Cloth API",
        default_version="v1",
        description="API for managing carts, orders, users, and goods",
        terms_of_service="https://example.com/terms/",
        contact=openapi.Contact(email="radin-04@mail.ru"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


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
       path('swagger/', schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
