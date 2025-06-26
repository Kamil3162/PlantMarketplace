from django.urls import path
from PlantMarketplace.authenticate.api.views import display_all_permissions

urlpatterns = [
    path('all/', display_all_permissions, name='user_permissions')
]