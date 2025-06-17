from django.urls import include, path
from views import base_view


urlpatterns = [
    path('inventory/', base_view, name='inventory'),
]