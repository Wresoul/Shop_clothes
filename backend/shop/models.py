from django.db import models
from django.urls import reverse


# Create your models here.
class Categories(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True,
                            verbose_name='URL', blank=True, null=True)

    class Meta:
        db_table = 'category'
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Goods(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200,
                            unique=True,
                            verbose_name='URL', blank=True, null=True)
    photo = models.ImageField(upload_to='shop_goods', blank=True)
    rating = models.FloatField(default=0)
    discount = models.DecimalField(default=0.00, max_digits=7,
                                   decimal_places=2, verbose_name='Скидка в %')
    price = models.DecimalField(default=0.00, max_digits=7,
                                decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    category = models.ForeignKey(to=Categories, on_delete=models.CASCADE)

    class Meta:
        db_table = 'product'
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("id",)

    def __str__(self):
        return f'{self.name} Количество - {self.quantity}'

    def get_absolute_url(self):
        return reverse("shop:product", kwargs={"product_slug": self.slug})

    def display_id(self):
        return f"{self.id:05}"

    def sell_price(self):
        if self.discount:
            return round(self.price - self.price * self.discount / 100, 2)

        return self.price
