from django.urls import path
from .views import users_list, user_detail, user_modify, reset_password, user_delete

urlpatterns = [
    path('all', users_list, name='users_list'),
    path('me', user_detail, name='user_detail'),
    path('modify', user_modify, name='user_modify'),
    path('reset-password', reset_password, name='reset_password'),
    path('<int:user_id>/delete/', user_delete, name='user_delete'),
]
