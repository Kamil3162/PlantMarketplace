# import os
# from django.conf import settings
# import django
#
# def pytest_configure():
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
#             'phonenumber_field',
#             'account.apps.UserManagementConfig',
#             'authentication',
#             'bargain',
#             'chat',
#             'core',
#             'offers',
#             'orders',
#             'payments',
#             'permissions',
#             'plant_marketplace',
#             'plants',
#             'products',
#             'shipments',
#         ],
#         # SECRET_KEY='django-insecure-^fabn--2*9$h1lx(5tb&uuc8fog$%-^l57n527zw%sdeh=w(ne'
#     )
#     # django.setup()
