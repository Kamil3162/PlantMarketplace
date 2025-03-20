from django.urls import path
from .views import product_create, product_list, product_detail

urlpatterns = [
    path('product/', product_create, name='product_create'),
    path('product-list/', product_list, name='product_list'),
    path('product-detail/<str:product_uuid>/', product_detail, name='product_detail'),
    # path('product-delete/<int:product_id>', product_create, name='product_create'),
]