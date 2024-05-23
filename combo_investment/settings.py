"""
Django settings for combo_investment project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path
from zoneinfo import ZoneInfo

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-*6815$8huknfe(7d&j=la)cdzjralyi2*&ph1_h3a@ai2f51u("

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "drf_yasg",
    "drf_spectacular",
    "django_filters",
    "django_extensions",
    "dashboard",
    "datahub",
    "data_import",
    "users",
    "industries",
    "user_investment",
    "scrapper",
    "news",
    "mutual_funds",
    "groww",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "combo_investment.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "combo_investment.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    # "default": {
    #     "ENGINE": "django.db.backends.postgresql",
    #     "NAME": "investment_db",
    #     "USER": "admin",
    #     "PASSWORD": "admin",
    #     "HOST": "localhost",
    #     "PORT": 5436,
    # },
    "default": {
        "ENGINE": os.getenv("DATABASE_ENGINE"),
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": os.getenv("DATABASE_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

# AWS_ACCESS_KEY_ID = "your-access-key-id"
# AWS_SECRET_ACCESS_KEY = "your-secret-access-key"
# AWS_STORAGE_BUCKET_NAME = "your-bucket-name"
# AWS_S3_REGION_NAME = "your-region-name"  # e.g., 'us-west-1'
#
# DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "console": {
#             "level": "DEBUG",
#             "class": "logging.StreamHandler",
#         },
#     },
#     "loggers": {
#         "": {
#             "handlers": ["console"],
#             "level": "DEBUG",
#             "propagate": True,
#         },
#     },
# }


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "COMPONENT_SPLIT_REQUEST": True,
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {"Basic": {"type": "basic"}},
    "REFETCH_SCHEMA_WITH_AUTH": True,
    "COMPONENT_SPLIT_REQUEST": True,
    # "DEFAULT_AUTO_SCHEMA_CLASS": "combo_investment.swagger.CustomAutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Combo Investment API",
    "DESCRIPTION": "",
    "VERSION": "0.1.0",
    "SERVE_PERMISSIONS": [
        (
            "rest_framework.permissions.AllowAny"
            if DEBUG
            else "rest_framework.permissions.IsAuthenticated"
        )
    ],
    "COMPONENT_SPLIT_REQUEST": True,
}

CELERY_TIMEZONE = "Asia/Kolkata"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_DEFAULT_QUEUE = "default"
SCHEDULED_TASK_QUEUE = CELERY_TASK_DEFAULT_QUEUE
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
TIME_ZONE = "Asia/Kolkata"

# CORS
CORS_ORIGIN_WHITELIST = [
    "http://127.0.0.1:3000",
]


# Celery Configuration Options
CELERY_WORKER_CONCURRENCY = os.getenv("CELERY_WORKER_CONCURRENCY")
CELERY_WORKER_SEND_TASK_EVENT = False
CELERY_TASK_DEFAULT_QUEUE = os.getenv("CELERY_TASK_DEFAULT_QUEUE", "default")
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_IGNORE_RESULT = True
CELERY_TASK_SOFT_TIME_LIMIT = 300
CELERY_IMPORTS = [
    "datahub.tasks",
]
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

NSE_BASE_URL = "https://www.nseindia.com"
NSE_HISTORICAL_DATA_API_URL = "https://www.nseindia.com/api/historical/cm/equity"
NSE_SEARCH_SYMBOL_API_URL = "https://www.nseindia.com/api/search/autocomplete?q="
NSE_SYMBOL_QUOTE_API_URL = "https://www.nseindia.com/api/quote-equity?symbol="
NSE_STOCK_INDICES_API_URl = "https://www.nseindia.com/api/allIndices"
NSE_STOCK_INDEX_DETAIL_API_URL = (
    "https://www.nseindia.com/api/equity-stockIndices?index="
)
NSE_UPCOMING_EVENTS_API_URL = "https://www.nseindia.com/api/event-calendar?"


GROWW_MF_INVESTMENT_DASHBOARD = "https://groww.in/v1/api/aggregator/v2/dashboard"
GROWW_MF_SCHEME_DETAILS = "https://groww.in/v1/api/bse/v1/scheme/details"
GROWW_SCHEME_TRANSACTIONS = (
    "https://groww.in/v1/api/portfolio/v1/transaction/scheme/all"
)
