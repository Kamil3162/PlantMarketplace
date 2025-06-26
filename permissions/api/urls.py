from django.urls import path

from .views import get_permissions
urlpatterns = [
    path('permissions/', get_permissions, name='permissions'),
]