import json
import ssl
import smtplib
import logging
import time

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

    time_start = time.perf_counter_ns()
    redis_time = redis_manager.get_client().time()

    # final exec time
    final_time = time.perf_counter_ns()

    print(f"exec time = {final_time - time_start}")

    logger.info("💾 Attempting to save data to Redis...")
    redis_manager.insert_data(task_data)
    logger.info("✅ Task 'set_auth_user_data' completed successfully")

