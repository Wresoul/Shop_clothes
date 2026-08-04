from django.db import models
from shop.models import Goods
from users.models import User


# Create your models here.
class CartQueryset(models.QuerySet):

    def total_price(self):
        total_price = sum(cart.products_price() for cart in self)
        return total_price

    def total_quantity(self):
        if self:
            total_quantity = sum(cart.quantity for cart in self)
            return total_quantity
        return 0


class Cart(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             blank=True, null=True,
                             verbose_name='Пользователь')
    product = models.ForeignKey(to=Goods,
                                on_delete=models.CASCADE,
                                verbose_name='Товар')
    quantity = models.PositiveSmallIntegerField(default=0,
                                                verbose_name='Количество')
    session_key = models.CharField(max_length=32,
                                   null=True,
                                   blank=True)
    created_timestamp = models.DateTimeField(auto_now_add=True,
                                             verbose_name='Дата добавления')

    class Meta:
        db_table = 'cart'
        verbose_name = "Корзину"
        verbose_name_plural = "Корзины"

    objects = CartQueryset().as_manager()

    def products_price(self):
        products_price = round(self.product.sell_price() * self.quantity, 2)
        return products_price

    def __str__(self):
        if self.user:
            return (f'Корзина {self.user.username} | '
                    f'Товар {self.product.name} | '
                    f'Количество {self.quantity}')

        return (f'Анонимная корзина | '
                f'Товар {self.product.name} | '
                f'Количество {self.quantity}')
