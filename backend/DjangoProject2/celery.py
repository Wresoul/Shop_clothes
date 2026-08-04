import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject2.settings')

app = Celery('DjangoProject2')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически загружаем задачи из всех приложений
app.autodiscover_tasks(['users', 'carts', 'orders', 'shop'])