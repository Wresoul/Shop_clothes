from django.db import models

# Create your models here.
class Categories(models.Model):
    name=models.CharField(max_length=100,unique=True, verbose_name='Название')
    slug=models.SlugField(max_length=200,unique=True, verbose_name='URL', blank=True, null=True)

    class Meta:
        db_table = 'category'
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'
    def __str__(self):
        return self.name

class Goods(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL', blank=True, null=True)
    photo = models.ImageField(upload_to='shop_goods', blank=True)
    rating = models.FloatField(default=0)
    discount = models.DecimalField(default=0.00, max_digits=7, decimal_places=2, verbose_name='Скидка в %')
    price = models.DecimalField(default=0.00, max_digits=7, decimal_places=2, verbose_name='Цена')
    category = models.ForeignKey(to=Categories, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Товары"