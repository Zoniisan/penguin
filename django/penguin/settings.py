"""
Django settings for penguin project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# django-environ
# https://pypi.org/project/django-environ/
import environ
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    SLACK_BACKEND=(str, 'django_slack.backends.ConsoleBackend'),
    STATIC_URL=(str, '/static/')
)
# reading .env file
environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# .env file に DEBUG 属性を書かなければ .env = True となる。
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third-party
    'bootstrap4',
    'bootstrap_datepicker_plus',
    'django_celery_beat',
    'django_celery_results',
    'django_select2',
    'django_slack',
    'ordered_model',
    'rest_framework_datatables',

    # penguin
    'home'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'penguin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'general', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'penguin.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    # read os.environ['DATABASE_URL'] and
    # raises ImproperlyConfigured exception if not found
    'default': env.db(),
}

# Logging Settings
# https://docs.djangoproject.com/en/3.1/topics/logging/
LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'slack_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django_slack.log.SlackExceptionHandler',
        },
    },
    'loggers': {
        'django': {
            'level': 'ERROR',
            'handlers': ['slack_admins'],
        },
    },
}

AUTH_USER_MODEL = 'home.User'

AUTHENTICATION_BACKENDS = [
    'penguin.auth.NoPasswordBackend'
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = False

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = env('STATIC_URL')
STATIC_ROOT = 'static'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'general', 'static')
]

# Email Settings
# https://docs.djangoproject.com/ja/3.1/topics/email/
# 暫定的に標準出力へ吐き出す
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_FROM = 'penguin-noreply@example.com'

# Useful Constants
BASE_URL = env('BASE_URL')

# Datetime Format
DATETIME_FORMAT = 'Y/m/d H:i:s'
DATE_FORMAT = 'Y/m/d'

# django-rest-framework-datatables
# https://pypi.org/project/djangorestframework-datatables/

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': (
        'rest_framework_datatables.pagination.DatatablesPageNumberPagination'
    ),
    'PAGE_SIZE': 50,
}

# django-redis / django-select2
# https://pypi.org/project/django-redis/
# https://pypi.org/project/django-select2/

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# celery
# https://pypi.org/project/celery/
CELERY_TIMEZONE = 'Asia/Tokyo'
CELERY_BROKER_URL = 'redis://redis:6379'

# django-celery-results
# https://pypi.org/project/django-celery-results/
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'

# django-slack
# https://django-slack.readthedocs.io/
SLACK_BACKEND = env('SLACK_BACKEND')

# ConsoleBackend を利用する場合は slack 関連の設定を省略
if SLACK_BACKEND != 'django_slack.backends.ConsoleBackend':
    SLACK_BACKEND_FOR_QUEUE = env('SLACK_BACKEND_FOR_QUEUE')
    SLACK_TOKEN = env('SLACK_TOKEN')
    SLACK_CHANNEL = env('SLACK_CHANNEL')