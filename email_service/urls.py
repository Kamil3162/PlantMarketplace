from django.urls import path

from views import create_brand_new_email_query

urlpatterns = [
    path('base/', create_brand_new_email_query, name='test')
]