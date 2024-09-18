import os
from pathlib import Path

#Пути внутри приложения
BASE_DIR = Path(__file__).resolve().parent.parent


#Ключ
SECRET_KEY = 'django-insecure-ka9lprsmp9(m^cm^iiyp-&p%lm8&zum*@1#sf1misywbeqoxq^'

#Включения дебаг
DEBUG = True

#Имена хостов
ALLOWED_HOSTS = []


#Установленные приложения django
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mptt',
    'shop.apps.ShopConfig',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

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
                'shop.context_processors.categories',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'


#Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


#Проверка пароля админки
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


#Регион и язык приложения
LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


#Фильтр статичных данных (CSS,JV,Картинок)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'media/static'),
]

#Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#Аутентификация
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

#URL для перенаправления после входа
LOGIN_REDIRECT_URL = 'index'

#URL для перенаправления после выхода
LOGOUT_REDIRECT_URL = 'index'

#Месенджы входа
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


SESSION_ENGINE = 'django.contrib.sessions.backends.db'
CART_SESSION_ID = 'cart'

#Логирование
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}


#Django-Payments для тестовой оплаты
PAYMENT_VARIANTS = {
    'default': ('payments.dummy.DummyProvider', {
        'secret': 'test_secret_key_souvenir_shop_muiv',
    })
}

#Хост платежей
PAYMENT_HOST = '127.0.0.1:8000'

#Модель платежа
PAYMENT_MODEL = 'shop.Payment'