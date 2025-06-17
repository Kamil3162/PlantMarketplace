import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

print("execute settings email service")
print(BASE_DIR)
print("execute settings email service")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = os.environ.get('DEBUG', 'False').lower() == 'false'
DEBUG = True

CORS_ALLOW_ALL_ORIGINS = True  # TYLKO DO TESTÓW!

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'email-service',    # ← DODAJ container name!
    '0.0.0.0',         # ← DODAJ dla Docker
    '*',
    'gateway-gateway-app-1'# ← Tymczasowo dla debug
]
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    # 'django_celery_beat',  # For scheduled tasks
    # 'django_celery_results',  # For storing task results in database
    # Local apps
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
AUTH_USER_MODEL = 'data.CustomUser'  # ← DODAJ TO

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

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'mydatabase1'),     # ← ZMIEŃ z 'email_db'
        'USER': os.environ.get('POSTGRES_USER', 'myuser'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'mypassword'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),           # ← ZMIEŃ z 'email_db'
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# Cache configuration (useful for rate limiting and other features)
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': os.environ.get('REDIS_URL', 'redis://redis:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Warsaw'  # Match your ConfigCelery timezone
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'youremail@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('APP_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'youremail@gmail.com')

# Celery Configuration
# RabbitMQ as broker
RABBITMQ_USER = os.environ.get('RABBITMQ_DEFAULT_USER', 'myuser')
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_DEFAULT_PASS', 'mypassword')
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT', '5672')
CELERY_BROKER_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//'

# Redis as result backend (stores task results)
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'django-db')

# Serialization format
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Time zone settings
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Task-specific settings
CELERY_TASK_ACKS_LATE = True  # Tasks are acknowledged after execution
CELERY_TASK_REJECT_ON_WORKER_LOST = True  # Tasks are re-queued if worker dies
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # Retry after 1 minute by default
CELERY_TASK_MAX_RETRIES = 3  # Maximum number of retries

# Define queues for different types of email tasks
CELERY_TASK_ROUTES = {
    'email_service.tasks.send_newsletter': {'queue': 'newsletters'},
    'email_service.tasks.send_email': {'queue': 'transactional'},
    'email_service.tasks.send_notification': {'queue': 'notifications'},
}

# Prefetch settings - how many tasks a worker can reserve at once
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Process one task at a time

# Rate limiting to prevent email flooding
CELERY_TASK_ANNOTATIONS = {
    'email_service.tasks.send_email': {
        'rate_limit': '60/m',  # 60 emails per minute
    },
    'email_service.tasks.send_newsletter': {
        'rate_limit': '1/m',  # 1 newsletter batch per minute
    },
}

# Beat schedule for periodic tasks (if you need scheduled emails)
CELERY_BEAT_SCHEDULE = {
    'cleanup-old-email-logs': {
        'task': 'email_service.tasks.cleanup_old_email_logs',
        'schedule': timedelta(days=1),  # Run once per day
        'kwargs': {'days_to_keep': 90},  # Keep 90 days of logs
    },
    # Add other scheduled email tasks here
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'email_service.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'email_service': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

# API settings (if you're exposing an API)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/hour',
        'user': '100/hour'
    }
}

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