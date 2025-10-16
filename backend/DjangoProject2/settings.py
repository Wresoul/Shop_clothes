import os.path
import logging
from pathlib import Path
from pythonjsonlogger import jsonlogger
import environ
from broker.producer import send_to_kafka




# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
env.read_env(ENV_DIR / '.env')

KAFKA_BOOTSTRAP_SERVERS = env('KAFKA_BOOTSTRAP_SERVERS', default='localhost:9192')
KAFKA_TOPICS = {
    'logs': env('KAFKA_TOPIC_LOGS', default='logs-topic'),
    'orders': env('KAFKA_TOPIC_ORDERS', default='orders-topic'),
    'carts': env('KAFKA_TOPIC_CARTS', default='carts-topic'),
    'celery': env('KAFKA_TOPIC_CELERY', default='celery'),
}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

SECRET_KEY = env('SECRET_KEY', default='django-insecure-3q7npl0dc4j$2nb-j0988&Ffdsce5MAx4cdsw(_)xhi$fy')

DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    '127.0.0.1',
    'localhost'
])

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://*.127.0.0.1'
])

# Application definition
INSTALLED_APPS = [
    'main',
    'shop',
    'users',
    'orders',
    'carts',
    'broker',
    'core',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'debug_toolbar',
    'rest_framework',
    'drf_yasg',
    'django_redis',
    'social_django',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'DjangoProject2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',  # Для social-auth
                'social_django.context_processors.login_redirect',  # Для social-auth
            ],
        },
    },
]

WSGI_APPLICATION = 'DjangoProject2.wsgi.application'

# Database (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env.int('POSTGRES_PORT', default=5432),
    }
}

# MongoDB settings
MONGO_URI = env('MONGO_URI', default='mongodb://localhost:27017/')
MONGO_DATABASE = env('MONGO_DATABASE', default='kafka_db')

from broker.logging_handlers import KafkaLoggingHandler, NoKafkaFilter

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'filters': {
        'no_kafka': {
            '()': NoKafkaFilter,  # Теперь из импорта
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'verbose',
        },
        'kafka': {
            'class': 'broker.logging_handlers.KafkaLoggingHandler',  # Реальный путь к классу
            'level': 'INFO',
            'filters': ['no_kafka'],
        },
    },
    'loggers': {
        'broker.producer': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'broker': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {  # Root
            'handlers': ['console', 'kafka'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Redis Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': env('REDIS_PASSWORD')
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 3
}

# Internationalization
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'
LOGIN_URL = '/user/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Stripe
# STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY')
# STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
# STRIPE_API_VERSION = env('STRIPE_API_VERSION')

# Celery settings
CELERY_BROKER_URL = env('CELERY_BROKER_URL')  # Kafka broker address
CELERY_RESULT_BACKEND = env('REDIS_URLWITHPASSWORD')  # Redis backend with password
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 10 * 60
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_DEFAULT_QUEUE = 'celery'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


# Social Auth
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env('OATH_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env('OATH_CLIENT_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/users/profile/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/users/login/'
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'redirect_uri': 'http://127.0.0.1:8000/auth/complete/google-oauth2/',
}

