import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')
DEBUG = True

CSRF_TRUSTED_ORIGINS=[
    "http://api-gateway:8010",
    "http://localhost:8010",
    'http://127.0.0.1:8010',
]

CORS_ALLOW_ALL_ORIGINS = True  # TYLKO DO TESTÓW!


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '*',
]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'data'
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'authdb1'),
        'USER': os.environ.get('POSTGRES_USER', 'authadmin'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'authpassword'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.authenticate.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.authenticate.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.authenticate.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.authenticate.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Warsaw'  # Match your ConfigCelery timezone
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Create logs directory if it doesn't exist
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)


# Security settings for production
if not DEBUG:
    # HTTPS settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Content Security Policy
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

CONSUL_NAME = 'consul_client'
CONSUL_PORT = os.getenv('CONSUL_PORT', '8500')