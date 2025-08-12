from django.urls import path

from .views import create_brand_new_email_query, send_reset_link, crete_account_modification_email

urlpatterns = [
    path('base/', create_brand_new_email_query, name='test'),
    path('reset/', send_reset_link, name='reset'),
    path('send/', crete_account_modification_email, name='modify')
]