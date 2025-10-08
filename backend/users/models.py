from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    image = models.ImageField(upload_to='users_images',
                              blank=True, null=True, verbose_name='Аватар')
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    is_image_processed = models.BooleanField(default=False, verbose_name='Изображение обработано')
    is_external_authenticated = models.BooleanField(default=False, verbose_name='Внешняя аутентификация подтверждена')
    external_token = models.CharField(max_length=500, blank=True, null=True, verbose_name='Внешний токен')

    class Meta:
        db_table = 'user'
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
