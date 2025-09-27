from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

app_name = 'users'

urlpatterns = [
    path('login/', cache_page(60*5)(views.login), name='login'),
    path('registration/', views.registration, name='registration'),
    path('profile/', views.profile, name='profile'),
    path('users-cart/', views.users_cart, name='users_cart'),
    path('logout/', views.logout, name='logout'),
]
