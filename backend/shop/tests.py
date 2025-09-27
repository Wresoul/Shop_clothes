from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Categories, Goods
from .utils import q_search
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import shutil


class TestStorage(FileSystemStorage):
    def __init__(self):
        super().__init__(location=settings.MEDIA_ROOT)


class CategoriesModelTest(TestCase):
    def setUp(self):
        # Очищаем базу и создаем категорию
        Categories.objects.all().delete()
        self.category = Categories.objects.create(
            name="Электроника",
            slug="electronics"
        )

    def test_category_creation(self):
        # Проверяем создание категории
        category = Categories.objects.get(slug="electronics")
        self.assertEqual(category.name, "Электроника")
        self.assertEqual(category.slug, "electronics")

    def test_category_str(self):
        # Проверяем метод __str__
        self.assertEqual(str(self.category), "Электроника")

    def test_category_unique_slug(self):
        # Проверяем уникальность slug
        from django.db.utils import IntegrityError
        with self.assertRaises(IntegrityError):
            Categories.objects.create(name="Другая", slug="electronics")


class GoodsModelTest(TestCase):
    def setUp(self):
        # Настраиваем временное хранилище для медиа
        self.media_root = os.path.join(settings.BASE_DIR, 'test_media')
        os.makedirs(self.media_root, exist_ok=True)
        settings.MEDIA_ROOT = self.media_root
        self.storage = TestStorage()

        # Создаем категорию и товар
        Categories.objects.all().delete()
        Goods.objects.all().delete()
        self.category = Categories.objects.create(
            name="Электроника",
            slug="electronics"
        )
        self.goods = Goods.objects.create(
            name="Телефон",
            slug="phone",
            photo=SimpleUploadedFile("phone.jpg", b"file_content", content_type="image/jpeg"),
            rating=4.5,
            discount=Decimal('10.00'),
            price=Decimal('1000.00'),
            quantity=5,
            category=self.category
        )

    def tearDown(self):
        # Очищаем медиафайлы и базу
        if os.path.exists(self.media_root):
            shutil.rmtree(self.media_root)
        Goods.objects.all().delete()
        Categories.objects.all().delete()

    def test_goods_creation(self):
        # Проверяем создание товара
        goods = Goods.objects.get(slug="phone")
        self.assertEqual(goods.name, "Телефон")
        self.assertEqual(goods.price, Decimal('1000.00'))
        self.assertEqual(goods.discount, Decimal('10.00'))
        self.assertEqual(goods.category, self.category)

    def test_goods_str(self):
        # Проверяем метод __str__
        self.assertEqual(str(self.goods), "Телефон Количество - 5")

    def test_goods_get_absolute_url(self):
        # Проверяем метод get_absolute_url
        expected_url = reverse("shop:product", kwargs={"product_slug": "phone"})
        self.assertEqual(self.goods.get_absolute_url(), expected_url)

    def test_goods_display_id(self):
        # Проверяем метод display_id
        self.assertEqual(self.goods.display_id(), f"{self.goods.id:05}")

    def test_goods_sell_price_with_discount(self):
        # Проверяем метод sell_price с учетом скидки
        self.assertEqual(self.goods.sell_price(), Decimal('900.00'))

    def test_goods_sell_price_no_discount(self):
        # Проверяем sell_price без скидки
        goods_no_discount = Goods.objects.create(
            name="Ноутбук",
            slug="laptop",
            price=Decimal('2000.00'),
            discount=Decimal('0.00'),
            category=self.category
        )
        self.assertEqual(goods_no_discount.sell_price(), Decimal('2000.00'))


class QSearchTest(TestCase):
    def setUp(self):
        # Создаем тестовые данные
        Categories.objects.all().delete()
        Goods.objects.all().delete()
        self.category = Categories.objects.create(
            name="Электроника",
            slug="electronics"
        )
        self.goods1 = Goods.objects.create(
            name="Телефон Samsung",
            slug="samsung-phone",
            price=Decimal('1000.00'),
            category=self.category
        )
        self.goods2 = Goods.objects.create(
            name="Ноутбук Dell",
            slug="dell-laptop",
            price=Decimal('2000.00'),
            category=self.category
        )

    def test_search_by_id(self):
        # Проверяем поиск по ID
        result = q_search(str(self.goods1.id))
        self.assertEqual(list(result), [self.goods1])

    def test_search_by_name(self):
        # Проверяем поиск по имени
        result = q_search("Samsung")
        self.assertEqual(list(result)[0].name, "Телефон Samsung")
        self.assertTrue("Samsung" in result[0].headline)


class CategoryViewSetTest(APITestCase):
    def setUp(self):
        # Создаем пользователя и категорию
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )
        self.client = APIClient()
        self.client.login(username="testuser", password="testpass")
        Categories.objects.all().delete()
        self.category = Categories.objects.create(
            name="Электроника",
            slug="electronics"
        )


    def test_retrieve_category(self):
        # Проверяем получение категории по slug
        response = self.client.get("/api/shop-categories/electronics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["slug"], "electronics")


class GoodsViewSetTest(APITestCase):
    def setUp(self):
        # Настраиваем временное хранилище
        self.media_root = os.path.join(settings.BASE_DIR, 'test_media')
        os.makedirs(self.media_root, exist_ok=True)
        settings.MEDIA_ROOT = self.media_root
        self.storage = TestStorage()

        # Создаем пользователя, категорию и товар
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )
        self.client = APIClient()
        self.client.login(username="testuser", password="testpass")
        Goods.objects.all().delete()
        Categories.objects.all().delete()
        self.category = Categories.objects.create(
            name="Электроника",
            slug="electronics"
        )
        self.goods = Goods.objects.create(
            name="Телефон",
            slug="phone",
            photo=SimpleUploadedFile("phone.jpg", b"file_content", content_type="image/jpeg"),
            price=Decimal('1000.00'),
            discount=Decimal('10.00'),
            category=self.category
        )

    def tearDown(self):
        # Очищаем медиафайлы и базу
        if os.path.exists(self.media_root):
            shutil.rmtree(self.media_root)
        Goods.objects.all().delete()
        Categories.objects.all().delete()

    def test_list_goods(self):
        # Проверяем список товаров
        response = self.client.get("/api/goods/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Телефон")
        self.assertEqual(response.data["results"][0]["sell_price"], float(900.00))

    def test_filter_by_category(self):
        # Проверяем фильтрацию по категории
        response = self.client.get("/api/goods/?category_slug=electronics")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Телефон")

    def test_filter_on_sale(self):
        # Проверяем фильтрацию товаров со скидкой
        response = self.client.get("/api/goods/?on_sale=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["discount"], "10.00")

    def test_search_goods(self):
        # Проверяем поиск по имени
        response = self.client.get("/api/goods/?q=Телефон")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Телефон")


class ShopViewsTest(TestCase):
    def setUp(self):
        # Настраиваем временное хранилище
        self.media_root = os.path.join(settings.BASE_DIR, 'test_media')
        os.makedirs(self.media_root, exist_ok=True)
        settings.MEDIA_ROOT = self.media_root
        self.storage = TestStorage()

        # Создаем тестовые данные
        Categories.objects.all().delete()
        Goods.objects.all().delete()
        self.category = Categories.objects.create(
            name="Электроника",
            slug="electronics"
        )
        self.goods = Goods.objects.create(
            name="Телефон",
            slug="phone",
            photo=SimpleUploadedFile("phone.jpg", b"file_content", content_type="image/jpeg"),
            price=Decimal('1000.00'),
            discount=Decimal('10.00'),
            category=self.category
        )

    def tearDown(self):
        # Очищаем медиафайлы и базу
        if os.path.exists(self.media_root):
            shutil.rmtree(self.media_root)
        Goods.objects.all().delete()
        Categories.objects.all().delete()

    def test_search_view(self):
        # Проверяем view search с категорией
        response = self.client.get(reverse("shop:index", kwargs={"category_slug": "electronics"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Телефон")

    def test_search_view_on_sale(self):
        # Проверяем фильтрацию по скидке
        response = self.client.get(reverse("shop:index", kwargs={"category_slug": "electronics"}) + "?on_sale=true")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Телефон")

    def test_search_view_query(self):
        # Проверяем поиск
        response = self.client.get(reverse("shop:index", kwargs={"category_slug": "electronics"}) + "?q=Телефон")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Телефон")

    def test_catalog_view(self):
        # Проверяем view catalog
        response = self.client.get(reverse("shop:catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Телефон")

    def test_product_view(self):
        # Проверяем view product
        response = self.client.get(reverse("shop:product", kwargs={"product_slug": "phone"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Телефон")
