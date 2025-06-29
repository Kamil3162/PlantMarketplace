import json
import ssl
import smtplib
import logging

from celery import Celery
from core.config import CeleryConfig
from cache.manager import RedisManager

# Create configuration
config_celery = CeleryConfig()
redis_manager = RedisManager()

app = Celery(config_celery.name)


# Configure Celery
app.conf.update(
    broker_url=config_celery.broker_url,
    task_serializer=config_celery.task_serializer,
    accept_content=config_celery.accept_content,
    result_serializer=config_celery.result_serializer,
    timezone=config_celery.timezone,
    enable_utc=config_celery.enable_utc
)
# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('celery_tasks.log', mode='a'),  # Zapisuje do pliku
        logging.StreamHandler()  # Wyświetla w konsoli
    ]
)

logger = logging.getLogger(__name__)


@app.task(bind=True, name='set_auth_user_data')
def set_auth_user_data(task_self, **task_data):
    logger.info("🚀 Task 'set_auth_user_data' started")

    logger.info("✅ JSON data parsed successfully")

    user_id = task_data['user_id']

    logger.info(f"👤 Processing user ID: {user_id}")

    logger.info("💾 Attempting to save data to Redis...")
    redis_manager.insert_data(task_data)
    logger.info("✅ Task 'set_auth_user_data' completed successfully")

"""
     The full contents of the message body was: body: '{"task": "set_auth_user_data", "id": "65c91bd6-b22c-4faa-a53d-536edb0d2943", 
     "args": [], 
     "kwargs": {"user_id": 5, "jti": "c77d75f8253f4492ac787667cd0b7733", "exp": 1751152908, "data_created": "2025-06-28 22:51:48.440509+00:00"}}' (228b)  
"""