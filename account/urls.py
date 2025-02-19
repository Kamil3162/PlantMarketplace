from django.conf.urls import url

urlpatterns = [
    path('/api/users', views.product_list, name='users_list'),
]
