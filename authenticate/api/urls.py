from django.urls import path
from .views import (
    login,
    logout,
    temporary_url,
    render_csrf_token,
    token_validate_url,
    ouath2uri,
    generate_reset_password_token,
    validate_reset_token
)


urlpatterns = [
    path('all/', login, name='user_permissions'),
    path('temporary/', temporary_url, name='temp_url'),
    path('render-csrf/', render_csrf_token, name='csrf-render'),
    path('login/', login, name='login'),
    path('token/', token_validate_url, name='token_validation'),
    path('oauth/', ouath2uri, name='oauth2uri'),
    path('reset/', generate_reset_password_token, name='reset_password_token'),
    path('validate/', validate_reset_token, name='validate_reset_token'),
]