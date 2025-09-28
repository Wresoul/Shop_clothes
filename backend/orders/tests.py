from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from .models import Order, OrderItem
from .forms import CreateOrderForm
from .serializers import OrderSerializer, OrderItemSerializer
from users.models import User
from shop.models import Goods, Categories
from carts.models import Cart
from django.forms import ValidationError

User = get_user_model()


class OrderModelTest(TestCase):
    def setUp(self):
        # Очищаем базу
        User.objects.all().delete()
        Categories.objects.all().delete()
        Goods.objects.all().delete()
        Order.objects.all().delete()
        OrderItem.objects.all().delete()

        # Создаём категорию, пользователя и товар
        self.category = Categories.objects.create(name="Тестовая категория")
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com",
            first_name="Иван", last_name="Иванов"
        )
        self.product = Goods.objects.create(
            name="Тестовый товар",
            category=self.category,
            price=Decimal("100.00"),
            quantity=10,
            discount=Decimal("0.00"),
            rating=0.0,
            slug="testovyy-tovar"
        )
        self.order = Order.objects.create(
            user=self.user,
            phone_number="1234567890",
            requires_delivery=True,
            delivery_address="ул. Тестовая, 1",
            payment_on_get=True,
            status="В обработке"
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            name=self.product.name,
            price=Decimal("100.00"),
            quantity=2
        )

    def test_order_creation(self):
        # Проверяем создание заказа
        order = Order.objects.get(id=self.order.id)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.phone_number, "1234567890")
        self.assertTrue(order.requires_delivery)
        self.assertEqual(order.delivery_address, "ул. Тестовая, 1")
        self.assertTrue(order.payment_on_get)
        self.assertFalse(order.is_paid)
        self.assertEqual(order.status, "В обработке")

    def test_order_str(self):
        # Проверяем метод __str__
        self.assertEqual(str(self.order), f"Заказ № {self.order.pk} | Покупатель Иван Иванов")

    def test_order_item_creation(self):
        # Проверяем создание элемента заказа
        item = OrderItem.objects.get(id=self.order_item.id)
        self.assertEqual(item.order, self.order)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.name, "Тестовый товар")
        self.assertEqual(item.price, Decimal("100.00"))
        self.assertEqual(item.quantity, 2)

    def test_order_item_products_price(self):
        # Проверяем метод products_price
        self.assertEqual(self.order_item.products_price(), Decimal("200.00"))

    def test_order_item_str(self):
        # Проверяем метод __str__
        self.assertEqual(str(self.order_item), f"Товар Тестовый товар | Заказ № {self.order.pk}")

    def test_orderitem_queryset_total_price(self):
        # Проверяем total_price в OrderitemQueryset
        items = OrderItem.objects.filter(order=self.order)
        self.assertEqual(items.total_price(), Decimal("200.00"))

    def test_orderitem_queryset_total_quantity(self):
        # Проверяем total_quantity в OrderitemQueryset
        items = OrderItem.objects.filter(order=self.order)
        self.assertEqual(items.total_quantity(), 2)


class OrderFormTest(TestCase):
    def test_create_order_form_valid(self):
        # Проверяем валидность формы
        form_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "phone_number": "1234567890",
            "requires_delivery": "1",
            "delivery_address": "ул. Тестовая, 1",
            "payment_on_get": "1"
        }
        form = CreateOrderForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["phone_number"], "1234567890")

    def test_create_order_form_invalid_phone(self):
        # Проверяем невалидный номер телефона
        form_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "phone_number": "123abc4567",
            "requires_delivery": "1",
            "delivery_address": "ул. Тестовая, 1",
            "payment_on_get": "1"
        }
        form = CreateOrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
        self.assertEqual(form.errors["phone_number"], ["Номер телефона должен содержать только цифры"])

    def test_create_order_form_invalid_phone_format(self):
        # Проверяем неверный формат номера телефона
        form_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "phone_number": "12345678",
            "requires_delivery": "1",
            "delivery_address": "ул. Тестовая, 1",
            "payment_on_get": "1"
        }
        form = CreateOrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
        self.assertEqual(form.errors["phone_number"], ["Неверный формат номера"])


class OrderSerializerTest(TestCase):
    def setUp(self):
        # Очищаем базу
        User.objects.all().delete()
        Categories.objects.all().delete()
        Goods.objects.all().delete()
        Order.objects.all().delete()
        OrderItem.objects.all().delete()

        # Создаём категорию, пользователя, товар, заказ и элемент заказа
        self.category = Categories.objects.create(name="Тестовая категория")
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.product = Goods.objects.create(
            name="Тестовый товар",
            category=self.category,
            price=Decimal("100.00"),
            quantity=10,
            discount=Decimal("0.00"),
            rating=0.0,
            slug="testovyy-tovar"
        )
        self.order = Order.objects.create(
            user=self.user,
            phone_number="1234567890",
            requires_delivery=True,
            delivery_address="ул. Тестовая, 1",
            payment_on_get=True
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            name=self.product.name,
            price=Decimal("100.00"),
            quantity=2
        )

    def test_order_item_serializer(self):
        # Проверяем сериализацию OrderItem
        serializer = OrderItemSerializer(self.order_item)
        data = serializer.data
        self.assertEqual(data["product"], "Тестовый товар")
        self.assertEqual(data["name"], "Тестовый товар")
        self.assertEqual(data["price"], "100.00")
        self.assertEqual(data["quantity"], 2)

    def test_order_serializer(self):
        # Проверяем сериализацию Order
        serializer = OrderSerializer(self.order)
        data = serializer.data
        self.assertEqual(data["user"], "testuser")
        self.assertEqual(data["phone_number"], "1234567890")
        self.assertTrue(data["requires_delivery"])
        self.assertEqual(data["delivery_address"], "ул. Тестовая, 1")
        self.assertTrue(data["payment_on_get"])
        self.assertFalse(data["is_paid"])
        self.assertEqual(data["status"], "В обработке")
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["total_price"], Decimal("200.00"))


class OrderViewSetTest(APITestCase):
    def setUp(self):
        # Очищаем базу
        User.objects.all().delete()
        Categories.objects.all().delete()
        Goods.objects.all().delete()
        Order.objects.all().delete()
        OrderItem.objects.all().delete()

        # Создаём категорию, пользователей, товар и заказ
        self.category = Categories.objects.create(name="Тестовая категория")
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.admin = User.objects.create_superuser(
            username="admin", password="adminpass123", email="admin@example.com"
        )
        self.product = Goods.objects.create(
            name="Тестовый товар",
            category=self.category,
            price=Decimal("100.00"),
            quantity=10,
            discount=Decimal("0.00"),
            rating=0.0,
            slug="testovyy-tovar"
        )
        self.order = Order.objects.create(
            user=self.user,
            phone_number="1234567890",
            requires_delivery=True,
            delivery_address="ул. Тестовая, 1",
            payment_on_get=True
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            name=self.product.name,
            price=Decimal("100.00"),
            quantity=2
        )
        self.client = APIClient()


    def test_retrieve_order(self):
        # Проверяем получение одного заказа
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("order-detail", kwargs={"pk": self.order.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], "testuser")
        self.assertEqual(len(response.data["items"]), 1)


class OrderViewsTest(TestCase):
    def setUp(self):
        # Очищаем базу
        User.objects.all().delete()
        Categories.objects.all().delete()
        Goods.objects.all().delete()
        Order.objects.all().delete()
        OrderItem.objects.all().delete()
        Cart.objects.all().delete()

        # Создаём категорию, пользователя, товар и корзину
        self.category = Categories.objects.create(name="Тестовая категория")
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com",
            first_name="Иван", last_name="Иванов"
        )
        self.product = Goods.objects.create(
            name="Тестовый товар",
            category=self.category,
            price=Decimal("100.00"),
            quantity=10,
            discount=Decimal("0.00"),
            rating=0.0,
            slug="testovyy-tovar"
        )
        self.cart_item = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )

    def test_create_order_get(self):
        # Проверяем отображение формы создания заказа
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("orders:create_order"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/create_order.html")
        self.assertIsInstance(response.context["form"], CreateOrderForm)
        self.assertEqual(response.context["form"].initial["first_name"], "Иван")
        self.assertEqual(response.context["form"].initial["last_name"], "Иванов")

    def test_create_order_post_valid(self):
        # Проверяем создание заказа
        self.client.login(username="testuser", password="testpass123")
        form_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "phone_number": "1234567890",
            "requires_delivery": "1",
            "delivery_address": "ул. Тестовая, 1",
            "payment_on_get": "1"
        }
        response = self.client.post(reverse("orders:create_order"), form_data)
        self.assertRedirects(response, reverse("users:profile"))
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(Cart.objects.count(), 0)  # Корзина очищена
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.phone_number, "1234567890")
        order_item = OrderItem.objects.first()
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, Decimal("100.00"))
        product = Goods.objects.get(id=self.product.id)
        self.assertEqual(product.quantity, 8)  # 10 - 2

    # def test_create_order_post_insufficient_quantity(self):
    #     # Проверяем ошибку при недостаточном количестве товара
    #     self.product.quantity = 1
    #     self.product.save()
    #     self.client.login(username="testuser", password="testpass123")
    #     form_data = {
    #         "first_name": "Иван",
    #         "last_name": "Иванов",
    #         "phone_number": "1234567890",
    #         "requires_delivery": "1",
    #         "delivery_address": "ул. Тестовая, 1",
    #         "payment_on_get": "1"
    #     }
    #     response = self.client.post(reverse("orders:create_order"), form_data)
    #     self.assertRedirects(response, reverse("carts:order"))
    #     self.assertEqual(Order.objects.count(), 0)
    #     self.assertEqual(OrderItem.objects.count(), 0)
    #     self.assertEqual(Cart.objects.count(), 1)  # Корзина не очищена
