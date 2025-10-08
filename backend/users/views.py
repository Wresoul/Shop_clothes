from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.db.models import Prefetch
from django.http import HttpResponseRedirect, JsonResponse
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
from .tasks import process_user_image, verify_external_auth
from social_django.utils import load_strategy, load_backend
import logging

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'phone_number']
    lookup_field = 'username'

    def get_permissions(self):
        if self.action in ['list', 'create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            external_token = form.cleaned_data.get('external_token')
            session_key = request.session.session_key
            if external_token:
                result = verify_external_auth.delay(None, external_token)
                request.session['external_auth_task_id'] = result.id
                messages.info(request, "Проверка внешней аутентификации запущена. Проверьте ваш email.")
                return HttpResponseRedirect(reverse('main:index'))
            else:
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = auth.authenticate(username=username, password=password)
                if user:
                    auth.login(request, user)
                    messages.success(request, f"{username}, Вы вошли в аккаунт")
                    if session_key:
                        Cart.objects.filter(session_key=session_key).update(user=user)
                    redirect_page = request.POST.get('next', None)
                    if redirect_page and redirect_page != reverse('users:logout'):
                        return HttpResponseRedirect(redirect_page)
                    return HttpResponseRedirect(reverse('main:index'))
                else:
                    messages.error(request, "Неверный логин или пароль")
        else:
            messages.error(request, "Ошибка в форме")
    else:
        form = UserLoginForm()
    context = {'title': 'Home - Авторизация', 'form': form}
    return render(request, 'users/login.html', context)

def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            session_key = request.session.session_key
            external_token = form.cleaned_data.get('external_token')
            if external_token:
                user = form.save(commit=False)
                user.set_unusable_password()
                user.save()
                result = verify_external_auth.delay(user.id, external_token)
                request.session['external_auth_task_id'] = result.id
                messages.info(request, "Регистрация успешна, проверка токена запущена. Проверьте ваш email.")
                if session_key:
                    Cart.objects.filter(session_key=session_key).update(user=user)
                return HttpResponseRedirect(reverse('main:index'))
            else:
                user = form.save()
                auth.login(request, user)
                if session_key:
                    Cart.objects.filter(session_key=session_key).update(user=user)
                messages.success(request, f"{user.username}, Вы успешно зарегистрированы и вошли в аккаунт")
                return HttpResponseRedirect(reverse('main:index'))
        else:
            messages.error(request, "Ошибка в форме")
    else:
        form = UserRegistrationForm()
    context = {'title': 'Home - Регистрация', 'form': form}
    return render(request, 'users/registration.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=request.user, files=request.FILES)
        if form.is_valid():
            user = form.save()
            if 'image' in request.FILES:
                process_user_image.delay(user.id, request.FILES['image'].name)
                messages.success(request, "Профиль обновлен, изображение обрабатывается")
            else:
                messages.success(request, "Профиль успешно обновлен")
            return HttpResponseRedirect(reverse('users:profile'))
    else:
        form = ProfileForm(instance=request.user)
    factory = APIRequestFactory()
    api_request = factory.get(
        reverse('user-detail', kwargs={'username': request.user.username}),
        HTTP_HOST='127.0.0.1:8000'
    )
    api_request.user = request.user
    view = UserViewSet.as_view({'get': 'retrieve'})
    response = view(api_request, username=request.user.username)
    user_data = response.data if response.status_code == 200 else {}
    orders = Order.objects.filter(user=request.user).prefetch_related(
        Prefetch('orderitem_set', queryset=OrderItem.objects.select_related('product'))
    )
    logger.info(f"Profile view accessed, user: {request.user.username}, session: {request.session.session_key}, messages: {list(messages.get_messages(request))}, test_key: {request.session.get('test_key')}")
    context = {
        'title': 'Home - Кабинет',
        'form': form,
        'user_data': user_data,
        'orders': orders,
    }
    return render(request, 'users/profile.html', context)

def users_cart(request):
    factory = APIRequestFactory()
    api_request = factory.get(reverse('user-detail', kwargs={'username': request.user.username}))
    api_request.user = request.user
    view = UserViewSet.as_view({'get': 'retrieve'})
    response = view(api_request, username=request.user.username)
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

def external_login(request):
    if request.method == 'POST':
        external_token = request.POST.get('external_token')
        if external_token:
            user = request.user if request.user.is_authenticated else None
            result = verify_external_auth.delay(user.id if user else None, external_token)
            request.session['external_auth_task_id'] = result.id
            messages.info(request, "Проверка аутентификации запущена. Проверьте ваш email.")
            return JsonResponse({'status': 'started', 'task_id': result.id})
        else:
            return JsonResponse({'status': 'error', 'message': 'Токен не предоставлен'})
    return render(request, 'users/external_login.html', {'title': 'Внешняя аутентификация'})

@login_required
def check_external_auth_status(request, task_id):
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    if result.ready():
        data = result.get()
        if data['status'] == 'success':
            messages.success(request, "Аутентификация подтверждена!")
            user = User.objects.get(id=data['user_id'])
            auth.login(request, user)
            return JsonResponse(data)
        else:
            messages.error(request, data['message'])
            return JsonResponse(data)
    return JsonResponse({'status': 'pending', 'message': 'Проверка в процессе...'})

def google_oauth_complete(request):
    logger.info(f"Google OAuth complete called, user authenticated before: {request.user.is_authenticated}, session: {request.session.session_key}")
    logger.info(f"Request GET params: {request.GET}")
    strategy = load_strategy(request)
    backend = load_backend(strategy, 'google-oauth2', redirect_uri='http://127.0.0.1:8000/auth/complete/google-oauth2/')
    try:
        user = backend.auth_complete(request=request)
        if user:
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            logger.info(f"User {user.username} authenticated, session: {request.session.session_key}, adding success message")
            request.session['test_key'] = 'test_value'
            request.session.modified = True
            messages.success(request, "Вход успешен!")
            logger.info(f"Session test_key in google_oauth_complete: {request.session.get('test_key')}")
            request.session.save()  # Явно сохраняем сессию
            return HttpResponseRedirect(reverse('users:profile'))
        else:
            logger.warning("User authentication failed")
            messages.error(request, "Ошибка входа через Google")
            return HttpResponseRedirect(reverse('users:login'))
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        messages.error(request, f"Ошибка входа через Google: {str(e)}")
        return HttpResponseRedirect(reverse('users:login'))