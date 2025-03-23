import os
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Базовые настройки
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'n3v8j2k9l1m2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Стандартные приложения Django:
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сторонние приложения:
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',            # автогенерация документации OpenAPI
    'silk',                      # анализ производительности (django-silk)
    'social_django',             # социальная авторизация

    # Ваше приложение:
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'silk.middleware.SilkyMiddleware',  # для django-silk
]

ROOT_URLCONF = 'procurement_project.urls'

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
                'social_django.context_processors.backends',  # для social auth
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'procurement_project.wsgi.application'

# Настройки базы данных (пример SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Пароли и валидация
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

# DRF и схема OpenAPI
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
         'rest_framework.authentication.TokenAuthentication',
         'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
         'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
         'user': '100/minute',
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Procurement Project API',
    'DESCRIPTION': 'Документация API для проекта автоматизации закупок',
    'VERSION': '1.0.0',
}

# Кэширование (пример django-cacheops)
CACHEOPS_REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 1,
    'socket_timeout': 3,
}
CACHEOPS = {
    'orders.product': {'ops': 'all', 'timeout': 60*15},
}

# Социальная авторизация (пример для Google OAuth2)
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Инициализация Sentry (замените DSN на ваш)
sentry_sdk.init(
    dsn="https://6199de63790ac62c8ba047ee6a6c0d6e@o4509014817112064.ingest.de.sentry.io/4509014819405904",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)

# Настройки Celery (брокер Redis)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# ВАЖНО: Используем кастомную модель пользователя из orders
AUTH_USER_MODEL = 'orders.User'
