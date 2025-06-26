from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authenticate'

class DataConfig(AppConfig):  # ← Zmień nazwę klasy
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data'  # ← To musi odpowiadać folderowi
    label = 'data'