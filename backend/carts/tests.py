from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from carts.models import Cart
from carts.serializers import CartSerializer
from shop.models import Goods, Categories
from users.models import User
from django.test.client import RequestFactory
from carts.utils import get_user_carts
from django.template.loader import render_to_string
import json

User = get_user_model()

class CartModelTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.category = Categories.objects.create(name="Тестовая категория", slug="test-category")
        self.product = Goods.objects.create(
            name="Тестовый товар",
            category=self.category,
            price=Decimal("100.00"),
            quantity=10,
            discount=Decimal("0.00"),
            rating=0.0,
            slug="testovyy-tovar"
        )
        self.cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )
        # Для анонимной корзины
        self.client.get('/')  # Создаём session_key
        self.session_key = self.client.session.session_key
        self.anonymous_cart = Cart.objects.create(
            session_key=self.session_key,
            product=self.product,
            quantity=3
        )

    def test_cart_creation_authenticated(self):
        cart = Cart.objects.get(id=self.cart.id)
        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.product, self.product)
        self.assertEqual(cart.quantity, 2)
        self.assertIsNotNone(cart.created_timestamp)

    def test_cart_creation_anonymous(self):
        cart = Cart.objects.get(id=self.anonymous_cart.id)
        self.assertIsNone(cart.user)
        self.assertEqual(cart.session_key, self.session_key)
        self.assertEqual(cart.product, self.product)
        self.assertEqual(cart.quantity, 3)

    def test_cart_str_authenticated(self):
        self.assertEqual(
            str(self.cart),
            f"Корзина testuser | Товар Тестовый товар | Количество 2"
        )

    def test_cart_str_anonymous(self):
        self.assertEqual(
            str(self.anonymous_cart),
            f"Анонимная корзина | Товар Тестовый товар | Количество 3"
        )

    def test_cart_products_price(self):
        self.assertEqual(self.cart.products_price(), Decimal("200.00"))

    def test_cart_queryset_total_price(self):
        carts = Cart.objects.filter(user=self.user)
        self.assertEqual(carts.total_price(), Decimal("200.00"))

    def test_cart_queryset_total_quantity(self):
        carts = Cart.objects.filter(user=self.user)
        self.assertEqual(carts.total_quantity(), 2)

    def test_cart_queryset_total_quantity_empty(self):
        Cart.objects.all().delete()
        carts = Cart.objects.filter(user=self.user)
        self.assertEqual(carts.total_quantity(), 0)

class CartViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.category = Categories.objects.create(name="Тестовая категория", slug="test-category")
        self.product = Goods.objects.create(
            name="Тестовый товар",
            category=self.category,
            price=Decimal("100.00"),
            quantity=10,
            discount=Decimal("0.00"),
            rating=0.0,
            slug="testovyy-tovar"
        )
        self.cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )
        # Для анонимной корзины
        self.client.get('/')  # Создаём session_key
        self.session_key = self.client.session.session_key

    def test_cart_add_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("carts:cart_add"),
            {"product_id": self.product.id}
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["message"], "Товар добавлен в корзину")
        self.assertIn("cart_items_html", response_data)
        cart = Cart.objects.get(user=self.user, product=self.product)
        self.assertEqual(cart.quantity, 3)  # 2 + 1

    def test_cart_add_anonymous(self):
        response = self.client.post(
            reverse("carts:cart_add"),
            {"product_id": self.product.id}
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["message"], "Товар добавлен в корзину")
        self.assertIn("cart_items_html", response_data)
        cart = Cart.objects.get(session_key=self.session_key, product=self.product)
        self.assertEqual(cart.quantity, 1)

    def test_cart_change(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("carts:cart_change"),
            {"cart_id": self.cart.id, "quantity": 5}
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["message"], "Количество изменено")
        self.assertEqual(response_data["quantity"], 5)
        self.assertIn("cart_items_html", response_data)
        cart = Cart.objects.get(id=self.cart.id)
        self.assertEqual(cart.quantity, 5)

    def test_cart_change_invalid_quantity(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("carts:cart_change"),
            {"cart_id": self.cart.id, "quantity": "invalid"}
        )
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["error"], "Invalid quantity provided.")
        cart = Cart.objects.get(id=self.cart.id)
        self.assertEqual(cart.quantity, 2)  # Количество не изменилось

    def test_cart_remove(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("carts:cart_remove"),
            {"cart_id": self.cart.id}
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["message"], "Товар удален")
        self.assertEqual(response_data["quantity_deleted"], 2)
        self.assertIn("cart_items_html", response_data)
        self.assertFalse(Cart.objects.filter(id=self.cart.id).exists())

    def test_cart_remove_nonexistent(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("carts:cart_remove"),
            {"cart_id": 999}
        )
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["error"], "Cart item does not exist.")

class CartSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.category = Categories.objects.create(name="Тестовая категория", slug="test-category")
        self.product = Goods.objects.create(
            name="Тестовый товар",
            category=self.category,
            price=Decimal("100.00"),
            quantity=10,
            discount=Decimal("0.00"),
            rating=0.0,
            slug="testovyy-tovar"
        )
        self.cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )

    def test_cart_serializer(self):
        serializer = CartSerializer(self.cart)
        data = serializer.data
        self.assertEqual(data["id"], self.cart.id)
        self.assertEqual(data["product"], "Тестовый товар")
        self.assertEqual(data["quantity"], 2)
        self.assertEqual(data["products_price"], Decimal("200.00"))
        self.assertIsNotNone(data["created_timestamp"])

class CartViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="otherpass123", email="other@example.com"
        )
        self.category = Categories.objects.create(name="Тестовая категория", slug="test-category")
        self.product = Goods.objects.create(
            name="Тестовый товар",
            category=self.category,
            price=Decimal("100.00"),
            quantity=10,
            discount=Decimal("0.00"),
            rating=0.0,
            slug="testovyy-tovar"
        )
        self.cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )
        self.other_cart = Cart.objects.create(
            user=self.other_user,
            product=self.product,
            quantity=1
        )
