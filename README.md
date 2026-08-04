# Shop.co

Интернет-магазин одежды на Django. Помимо самого магазина (каталог, корзина,
заказы, регистрация/логин, в том числе через Google) в проекте настроен
конвейер событий: действия пользователей (заказы, корзина, логи) улетают в
Kafka, отдельный сервис `message-processor` их вычитывает и складывает в
MongoDB — то есть в репозитории фактически два независимых Python-приложения
(Django-бэкенд и консьюмер Kafka), плюс инфраструктура для продакшена
(Nginx + Let's Encrypt).

## Стек

- **Backend**: Django 5.1, Django REST Framework, drf-yasg (Swagger)
- **БД**: PostgreSQL
- **Кэш/сессии**: Redis (`django-redis`), сессии Django хранятся в кэше
- **Фоновые задачи**: Celery (брокер — тот же Redis)
- **Событийный стриминг**: Kafka → отдельный сервис `message-processor` → MongoDB
- **Аутентификация**: Django auth + Google OAuth2 (`social-auth-app-django`)
- **Инфраструктура**: Docker Compose, Nginx, Certbot (Let's Encrypt)

## Как это устроено

```
Django (backend)
  │  post_save/post_delete на Order и Cart (backend/broker/signals.py)
  │  + логи через кастомный logging handler (backend/broker/logging_handlers.py)
  ▼
backend/broker/producer.py ──► Kafka (топики orders-topic, carts-topic, logs-topic)
                                    │
                                    ▼
                    message-processor/run_consumer.py (отдельный контейнер)
                                    │
                                    ▼
                                 MongoDB
```

Т.е. заказы и изменения корзины не только пишутся в PostgreSQL, но и
асинхронно логируются в MongoDB через Kafka — это фактически audit log/аналитика,
не критичная для работы магазина: если Kafka/Mongo недоступны, `producer.py`
просто ловит исключение и пишет в лог, сам магазин не падает.

## Структура репозитория

```
backend/                    Django-проект
  DjangoProject2/            settings, urls, celery.py, wsgi/asgi
  main/                      главная страница
  shop/                      каталог, категории, поиск, кэш карточки товара (Redis)
  users/                     регистрация/логин, профиль, Google OAuth2, обработка аватара (Celery)
  carts/                     корзина (add/change/remove)
  orders/                    оформление заказа
  broker/                    Kafka-продюсер + логирующий handler, отправка событий заказов/корзины
  core/                      общие декораторы/валидаторы/исключения
  fixtures/                  тестовые данные: категории, товары, пользователь
message-processor/          отдельный сервис — консьюмер Kafka, пишет в MongoDB
nginx/                       Dockerfile + nginx.conf (продакшен: HTTPS-редирект, TLS, проксирование на backend)
kafka_init_topics.sh         ручное создание топиков Kafka (см. ниже — запускать внутри контейнера kafka)
init-letsencrypt.sh          выпуск сертификатов Let's Encrypt для прод-домена (не в репозитории, только локально/на сервере)
docker-compose.yml           оркестрация всех сервисов
requirements.txt             дубликат backend/requirements.txt, реально не используется ни одним Dockerfile
```

## Сервисы docker-compose

| Сервис | Назначение |
|---|---|
| `backend` | Django (Gunicorn), при старте сам гоняет `makemigrations`, `migrate`, `collectstatic` |
| `db` | PostgreSQL |
| `redis` | кэш Django + брокер/backend для Celery |
| `celery` | воркер фоновых задач (обработка аватара, email-уведомления) |
| `kafka` | брокер событий, режим KRaft (без Zookeeper) |
| `mongodb` | хранилище обработанных Kafka-сообщений |
| `message-processor` | отдельное Python-приложение, консьюмер Kafka → MongoDB |
| `nginx` | реверс-прокси, TLS, раздача static/media — **только для продакшен-домена** |
| `certbot` | автопродление сертификатов Let's Encrypt каждые 12 часов |
| `connect`, `kafdrop`, `mongo-express` | веб-инструменты для отладки Kafka Connect / Kafka / MongoDB |

## Локальный запуск (для разработки, без TLS)

`nginx.conf` жёстко требует TLS-сертификат конкретного домена (`server_name your-domain.example`,
`ssl_certificate /etc/letsencrypt/live/your-domain.example/...`) — без выпущенного
сертификата контейнер `nginx` не поднимется. Для локальной разработки проще всего
поднять всё, кроме `nginx`/`certbot`, и ходить в Django напрямую на `:8000`.

1. Скопировать `.env.example` → `.env`, заполнить значения (см. раздел ниже).
2. Собрать образы и поднять инфраструктуру и приложение (без nginx/certbot):

   ```bash
   docker-compose build
   docker-compose up -d db redis kafka mongodb backend celery message-processor
   ```

   `backend` сам применит миграции и соберёт статику при старте — ждать это
   нужно (смотреть `docker-compose logs -f backend`), т.к. `depends_on` не
   гарантирует, что Kafka/Postgres реально готовы принимать соединения, а
   healthcheck настроен только для Kafka.
3. Загрузить тестовые данные (опционально):

   ```bash
   docker-compose exec backend python manage.py loaddata fixtures/shop/cats.json fixtures/shop/goods.json fixtures/users/users.json
   ```
4. Приложение: `http://localhost:8000`, Swagger: `http://localhost:8000/swagger/`,
   админка: `http://localhost:8000/admin/`.
5. Kafdrop (просмотр топиков/сообщений Kafka): `http://localhost:9000`,
   Mongo Express (просмотр MongoDB): `http://localhost:8081`.

### Топики Kafka

Топики создаются автоматически при первой отправке сообщения (если у брокера
включено `auto.create.topics.enable`) либо вручную скриптом
`kafka_init_topics.sh` — он не встроен ни в один Docker-образ, поэтому
выполнять его нужно внутри контейнера `kafka`:

```bash
docker cp kafka_init_topics.sh djangoproject2-kafka:/kafka_init_topics.sh
docker-compose exec kafka sh /kafka_init_topics.sh
```

Обратите внимание: скрипт создаёт `logs-topic`, `orders-topic`, `carts-topic`,
`auth-topic`, но реально в коде используются только первые три
(`backend/DjangoProject2/settings.py`, `KAFKA_TOPICS`) — `message-processor`
слушает тоже только эти три (`run_consumer.py`).

## Продакшен-запуск (с TLS)

1. В `nginx/nginx.conf` заменить `your-domain.example` на реальный домен.
2. Локально (не в репозитории) настроить `init-letsencrypt.sh` под свой домен/email
   и выполнить его — он создаст временный самоподписанный сертификат, поднимет
   `nginx`, затем запросит настоящий сертификат Let's Encrypt через webroot-проверку.
3. Поднять весь стек: `docker-compose up -d --build`.

## Google OAuth2

Для работы кнопки логина через Google нужен OAuth-клиент в
[Google Cloud Console](https://console.cloud.google.com/apis/credentials):
- Authorized redirect URI: `http://<host>/auth/complete/google-oauth2/`
  (для локальной разработки — `http://127.0.0.1:8000/auth/complete/google-oauth2/`,
  этот адрес также захардкожен в `SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS`
  в `settings.py`).
- Client ID/Secret положить в `.env` как `OATH_CLIENT_ID`/`OATH_CLIENT_SECRET`.

После успешной аутентификации `users/tasks.py` асинхронно (Celery) проверяет
токен и шлёт письмо-подтверждение (`EMAIL_BACKEND` в dev-режиме — консольный,
письма просто печатаются в лог `backend`/`celery`).

## API

REST API под префиксом `/api/`:

- `/api/users/`, `/api/goods/`, `/api/shop-categories/`, `/api/orders/`, `/api/carts/`
  — стандартные DRF ViewSet'ы (роутер в `backend/DjangoProject2/urls.py`).
- Swagger UI: `/swagger/`.

Помимо API есть классический server-rendered UI (Django templates) для
каталога, корзины, оформления заказа, регистрации/логина/профиля — это
основной способ пользоваться магазином, API — дополнительный слой.

## Переменные окружения

Обязательные (без значения по умолчанию, приложение не запустится без них):

```
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
REDIS_PASSWORD=
REDIS_URLWITHPASSWORD=        # redis://:<пароль>@redis:6379/<db> — используется как Celery result backend
CELERY_BROKER_URL=
OATH_CLIENT_ID=                # Google OAuth2 client id
OATH_CLIENT_SECRET=            # Google OAuth2 client secret
```

Опциональные (есть значение по умолчанию в `settings.py`):

```
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=
CSRF_TRUSTED_ORIGINS=
POSTGRES_PORT=5432
REDIS_URL=redis://localhost:6379/1
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=kafka_db
KAFKA_BOOTSTRAP_SERVERS=localhost:9192
KAFKA_TOPIC_LOGS=logs-topic
KAFKA_TOPIC_ORDERS=orders-topic
KAFKA_TOPIC_CARTS=carts-topic
KAFKA_TOPIC_CELERY=celery
```



