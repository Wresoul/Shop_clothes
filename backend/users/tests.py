from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User
from .forms import UserLoginForm, UserRegistrationForm, ProfileForm
from .serializers import UserSerializer
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import shutil


class TestStorage(FileSystemStorage):
    def __init__(self):
        super().__init__(location=settings.MEDIA_ROOT)


class UserModelTest(TestCase):
    def setUp(self):
        # Настраиваем временное хранилище
        self.media_root = os.path.join(settings.BASE_DIR, 'test_media')
        os.makedirs(self.media_root, exist_ok=True)
        settings.MEDIA_ROOT = self.media_root
        self.storage = TestStorage()

        # Очищаем базу и создаем пользователя
        User.objects.all().delete()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Иван",
            last_name="Иванов",
            phone_number="1234567890",
            image=SimpleUploadedFile("avatar.jpg", b"file_content", content_type="image/jpeg")
        )

    def tearDown(self):
        # Очищаем медиафайлы и базу
        if os.path.exists(self.media_root):
            shutil.rmtree(self.media_root)
        User.objects.all().delete()

    def test_user_creation(self):
        # Проверяем создание пользователя
        user = User.objects.get(username="testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Иван")
        self.assertEqual(user.last_name, "Иванов")
        self.assertEqual(user.phone_number, "1234567890")
        self.assertTrue(user.image)

    def test_user_str(self):
        # Проверяем метод __str__
        self.assertEqual(str(self.user), "testuser")


class UserFormsTest(TestCase):
    def setUp(self):
        # Очищаем базу и создаем пользователя для логина
        User.objects.all().delete()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )

    def test_user_login_form_valid(self):
        # Проверяем валидность формы логина
        form_data = {"username": "testuser", "password": "testpass123"}
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_login_form_invalid(self):
        # Проверяем невалидную форму логина
        form_data = {"username": "", "password": ""}
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("password", form.errors)

    def test_user_registration_form_valid(self):
        # Проверяем валидность формы регистрации
        form_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "username": "newuser",
            "email": "new@example.com",
            "password1": "testpass123",
            "password2": "testpass123"
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "new@example.com")

    def test_user_registration_form_invalid_passwords(self):
        # Проверяем несовпадение паролей
        form_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "username": "newuser",
            "email": "new@example.com",
            "password1": "testpass123",
            "password2": "differentpass"
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_profile_form_valid(self):
        # Проверяем валидность формы профиля
        form_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "username": "testuser",
            "email": "updated@example.com"
        }
        form = ProfileForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Иван")
        self.assertEqual(self.user.email, "updated@example.com")


class UserSerializerTest(TestCase):
    def setUp(self):
        # Настраиваем временное хранилище
        self.media_root = os.path.join(settings.BASE_DIR, 'test_media')
        os.makedirs(self.media_root, exist_ok=True)
        settings.MEDIA_ROOT = self.media_root
        self.storage = TestStorage()

        # Создаем пользователя
        User.objects.all().delete()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def tearDown(self):
        # Очищаем медиафайлы и базу
        if os.path.exists(self.media_root):
            shutil.rmtree(self.media_root)
        User.objects.all().delete()

    def test_user_serializer(self):
        # Проверяем сериализацию пользователя
        serializer = UserSerializer(self.user)
        data = serializer.data
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["orders"], [])
        self.assertEqual(data["cart_items"], [])
        self.assertEqual(data["total_cart_price"], 0)
        self.assertEqual(data["total_cart_quantity"], 0)


class UserViewSetTest(APITestCase):
    def setUp(self):
        # Сохраняем начальное количество пользователей
        self.initial_users = User.objects.count()
        # Создаем пользователей
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.admin = User.objects.create_superuser(
            username="admin", password="adminpass123", email="admin@example.com"
        )
        self.client = APIClient()


    def test_list_users_non_admin(self):
        # Проверяем доступ для не-админа
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user(self):
        # Проверяем получение профиля
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("user-detail", kwargs={"username": "testuser"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")


class UserViewsTest(TestCase):
    def setUp(self):
        # Настраиваем временное хранилище
        self.media_root = os.path.join(settings.BASE_DIR, 'test_media')
        os.makedirs(self.media_root, exist_ok=True)
        settings.MEDIA_ROOT = self.media_root
        self.storage = TestStorage()

        # Создаем пользователя
        User.objects.all().delete()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )

    def tearDown(self):
        # Очищаем медиафайлы и базу
        if os.path.exists(self.media_root):
            shutil.rmtree(self.media_root)
        User.objects.all().delete()

    def test_login_view_get(self):
        # Проверяем отображение формы логина
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")
        self.assertIsInstance(response.context["form"], UserLoginForm)

    def test_login_view_post_valid(self):
        # Проверяем успешный логин
        response = self.client.post(
            reverse("users:login"),
            {"username": "testuser", "password": "testpass123"}
        )
        self.assertRedirects(response, reverse("main:index"))
        self.assertTrue(self.client.session.get("_auth_user_id"))

    def test_login_view_post_invalid(self):
        # Проверяем невалидный логин
        response = self.client.post(
            reverse("users:login"),
            {"username": "testuser", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")
        self.assertFalse(self.client.session.get("_auth_user_id"))

    def test_registration_view_get(self):
        # Проверяем отображение формы регистрации
        response = self.client.get(reverse("users:registration"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/registration.html")
        self.assertIsInstance(response.context["form"], UserRegistrationForm)

    def test_registration_view_post_valid(self):
        # Проверяем успешную регистрацию
        form_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "username": "newuser",
            "email": "new@example.com",
            "password1": "testpass123",
            "password2": "testpass123"
        }
        response = self.client.post(reverse("users:registration"), form_data)
        self.assertRedirects(response, reverse("main:index"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertTrue(self.client.session.get("_auth_user_id"))

    def test_profile_view_get(self):
        # Проверяем отображение профиля
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")
        self.assertIsInstance(response.context["form"], ProfileForm)

    def test_profile_view_post_valid(self):
        # Проверяем обновление профиля
        self.client.login(username="testuser", password="testpass123")
        form_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "username": "testuser",
            "email": "updated@example.com"
        }
        response = self.client.post(reverse("users:profile"), data=form_data)
        self.assertRedirects(response, reverse("users:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updated@example.com")

    def test_users_cart_view(self):
        # Проверяем отображение корзины
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("users:users_cart"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/users_cart.html")
        self.assertEqual(response.context["cart_items"], [])
        self.assertEqual(response.context["total_cart_price"], 0)
        self.assertEqual(response.context["total_cart_quantity"], 0)

    def test_logout_view(self):
        # Проверяем выход
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("users:logout"))
        self.assertRedirects(response, reverse("main:index"))
        self.assertFalse(self.client.session.get("_auth_user_id"))
