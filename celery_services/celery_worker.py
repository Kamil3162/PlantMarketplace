import celery

# Używaj relatywnych importów
from .config import ConfigCelery, EmailConfig
from .celery_redis import CeleryOperations

config_celery = ConfigCelery()
ops_celery = CeleryOperations(config_celery)

app = ops_celery.app