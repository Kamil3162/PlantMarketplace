from django.urls import path, include
# from views import create_brand_new_email_query

import urls

urlpatterns = [
    path('email/', include(urls))
]