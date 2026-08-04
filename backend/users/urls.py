from django.urls import path, include
from django.views.decorators.cache import cache_page
from . import views


app_name = 'users'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('profile/', views.profile, name='profile'),
    path('users-cart/', views.users_cart, name='users_cart'),
    path('logout/', views.logout, name='logout'),
    path('external-login/', views.external_login, name='external_login'),
    path('check-external-auth/<str:task_id>/', views.check_external_auth_status, name='check_external_auth_status'),
]
