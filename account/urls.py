from django.urls import path
from .views import users_list, user_detail
urlpatterns = [
    path('/api/users', users_list, name='users_list'),
    path('/api/me', user_detail, name='user_detail'),
]
