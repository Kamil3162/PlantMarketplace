from django.urls import path, include

from .views import health_endpoint

urlpatterns = [
    path('', health_endpoint, name='health'),
]