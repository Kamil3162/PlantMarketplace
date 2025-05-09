from django.urls import path
from .views import product_create, product_list, product_detail
from .views_redis import redis_test_get, redis_test_delete
urlpatterns = [
    path('product/', product_create, name='product_create'),
    path('product-list/', product_list, name='product_list'),
    path('product-detail/<str:product_uuid>/', product_detail, name='product_detail'),
    path('redis-all', redis_test_get, name='redis_test_all'),
    path('redis-delete', redis_test_delete, name='redis_del_element'),

    # path('product-delete/<int:product_id>', product_create, name='product_create'),
]