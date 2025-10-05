from django.urls import path
from django.views.decorators.cache import cache_page
from . import views


app_name = 'users'

urlpatterns = [
    path('login/', cache_page(60*5)(views.login), name='login'),  # Кешируем на 5 мин
    path('registration/', views.registration, name='registration'),
    path('profile/', cache_page(60*15)(views.profile), name='profile'),  # Кешируем на 15 мин
    path('users-cart/', views.users_cart, name='users_cart'),  # Не кешируем (динамика)
    path('logout/', views.logout, name='logout'),
]
