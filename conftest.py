# import os
# from django.conf import settings
# import django
#
# def pytest_configure():
#     if not settings.configured:
#         settings.configure()
#
#     settings.configure(
#         DATABASES={
#             'default':{
#                 'ENGINE': 'django.db.backends.postgresql',
#                 'NAME': os.environ.get('POSTGRES_DB', 'testdatabase'),
#                 'USER': os.environ.get('POSTGRES_USER', 'testuser'),
#                 'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'testpassword'),
#                 'HOST': os.environ.get('POSTGRES_HOST', 'postgres_test'),
#                 'PORT': os.environ.get('POSTGRES_PORT', '5435'),
#                 'OPTIONS': {
#                     'connect_timeout': 5,
#                     'client_encoding': 'UTF8',
#                 },
#             }
#         },
#         INSTALLED_APPS=[
#             'django.contrib.admin',
#             'django.contrib.auth',
#             'django.contrib.contenttypes',
#             'django.contrib.sessions',
#             'django.contrib.messages',
#             'django.contrib.staticfiles',
#             'oauth2_provider',
#             'account.apps.UserManagementConfig',
#             'phonenumber_field',
#         ],
#         ROOT_URLCONF='plant_marketplace.urls',
#         AUTH_USER_MODEL='account.CustomUser',
#         DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
#         SECRET_KEY='test-key-not-for-production',
#         MIDDLEWARE=[
#             'django.middleware.security.SecurityMiddleware',
#             'django.contrib.sessions.middleware.SessionMiddleware',
#             'django.middleware.common.CommonMiddleware',
#             'django.middleware.csrf.CsrfViewMiddleware',
#             'django.contrib.auth.middleware.AuthenticationMiddleware',
#             'django.contrib.messages.middleware.MessageMiddleware',
#         ],
#     )
#     django.setup()
