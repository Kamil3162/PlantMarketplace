from django.apps import AppConfig

class UserManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'
    label = 'account'

class DataConfig(AppConfig):  # ← Zmień nazwę klasy
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data'  # ← To musi odpowiadać folderowi
    label = 'data'

