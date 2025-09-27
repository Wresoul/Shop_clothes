from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.test import APIRequestFactory
from .models import User
from .serializers import UserSerializer
from carts.models import Cart
from orders.models import Order, OrderItem
from .forms import ProfileForm, UserLoginForm, UserRegistrationForm

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'phone_number']
    lookup_field = 'username'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            session_key = request.session.session_key
            if user:
                auth.login(request, user)
                messages.success(request, f"{username}, Вы вошли в аккаунт")
                if session_key:
                    Cart.objects.filter(session_key=session_key).update(user=user)
                redirect_page = request.POST.get('next', None)
                if redirect_page and redirect_page != reverse('users:logout'):
                    return HttpResponseRedirect(request.POST.get('next'))
                return HttpResponseRedirect(reverse('main:index'))
    else:
        form = UserLoginForm()
    context = {'title': 'Home - Авторизация', 'form': form}
    return render(request, 'users/login.html', context)

def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            session_key = request.session.session_key
            user = form.instance
            auth.login(request, user)
            if session_key:
                Cart.objects.filter(session_key=session_key).update(user=user)
            messages.success(request, f"{user.username}, Вы успешно зарегистрированы и вошли в аккаунт")
            return HttpResponseRedirect(reverse('main:index'))
    else:
        form = UserRegistrationForm()
    context = {'title': 'Home - Регистрация', 'form': form}
    return render(request, 'users/registration.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=request.user, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Профайл успешно обновлен")
            return HttpResponseRedirect(reverse('users:profile'))
    else:
        form = ProfileForm(instance=request.user)
    factory = APIRequestFactory()
    api_request = factory.get(f'/api/users/{request.user.username}/')
    api_request.user = request.user
    view = UserViewSet.as_view({'get': 'retrieve'})
    response = view(api_request)
    user_data = response.data if response.status_code == 200 else {}
    context = {
        'title': 'Home - Кабинет',
        'form': form,
        'user_data': user_data,
    }
    return render(request, 'users/profile.html', context)

def users_cart(request):
    factory = APIRequestFactory()
    api_request = factory.get('/api/users/{request.user.username}/')
    api_request.user = request.user
    view = UserViewSet.as_view({'get': 'retrieve'})
    response = view(api_request)
    user_data = response.data if response.status_code == 200 else {}
    context = {
        'title': 'Home - Корзина',
        'cart_items': user_data.get('cart_items', []),
        'total_cart_price': user_data.get('total_cart_price', 0),
        'total_cart_quantity': user_data.get('total_cart_quantity', 0),
    }
    return render(request, 'users/users_cart.html', context)

@login_required
def logout(request):
    messages.success(request, f"{request.user.username}, Вы вышли из аккаунта")
    auth.logout(request)
    return redirect(reverse('main:index'))
