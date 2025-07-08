from .settings import *

SERVICE_NAME = 'product-service'


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'account',  # Jeśli potrzebujesz modelu użytkownika
    'products.redis_microservices',
]

# Konfiguracja bazy danych dla mikroserwisu produktowego
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PRODUCT_DB_NAME', 'product_service'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5435'),
    }
}


REDIS_HOST = os.environ.get('REDIS_HOST', 'product-redis')
REDIS_PORT = os.environ.get('REDIS_PORT', '6385')
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'product-rabbitmq')
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT', '5675')