from django.urls import path
from .views import (
    users_list,
    user_detail,
    user_modify,
    reset_password,
    user_delete,
    user_by_email,
    register,
    reset_link
)

urlpatterns = [
    path('all', users_list, name='users_list'),
    path('me', user_detail, name='user_detail'),
    path('modify', user_modify, name='user_modify'),
    path('reset-password', reset_password, name='reset_password'),
    path('user/email', user_by_email, name='user_by_email'),
    path('<int:user_id>/delete/', user_delete, name='user_delete'),
    path('register/', register, name='register'),
    path('reset/', reset_link, name='reset'),
]
