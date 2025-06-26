from django.urls import path
from . import views

urlpatterns = [
    path('', views.sign_in, name='sign_in'),
    path('sign-out', views.sign_out, name='sign_out'),
    path('authenticate-receiver', views.auth_receiver, name='auth_receiver'),
    path('test', views.url_test, name='url_test'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('test1', views.get_cookie_value, name='test'),
]