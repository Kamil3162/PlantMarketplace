import os
from dataclasses import dataclass, field
import dotenv

dotenv.load_dotenv()

@dataclass
class ConfigCelery:
    name: str = 'email-service'

    # RabbitMQ configuration
    broker_user: str = os.getenv('RABBITMQ_DEFAULT_USER', 'gateway_user')
    broker_password: str = os.getenv('RABBITMQ_DEFAULT_PASS', 'gateway_pass')
    broker_host: str = os.getenv('RABBITMQ_HOST', 'localhost')  # Use service name in docker
    broker_port: int = os.getenv('RABBITMQ_PORT', '5672')
    broker_url: str = f'amqp://{broker_user}:{broker_password}@{broker_host}:{broker_port}//'

    # For result backend, you could use Redis or PostgreSQL
    result_backend: str = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

    # Task settings
    task_serializer: str = 'json'
    accept_content: list = field(default_factory=lambda: ['json'])
    result_serializer: str = 'json'
    timezone: str = 'Europe/Warsaw'
    enable_utc: bool = True

    # Task routing - useful for different types of email tasks
    task_routes: dict = field(default_factory=lambda: {
        'send_newsletter': {'queue': 'newsletters'},
        'send_notification': {'queue': 'notifications'},
        'send_transactional': {'queue': 'transactional'}
    })

    # Retry settings
    task_acks_late: bool = True  # Tasks are acknowledged after execution
    task_reject_on_worker_lost: bool = True  # Tasks are re-queued if worker dies
    task_default_retry_delay: int = 60  # Retry after 1 minute
    task_max_retries: int = 3  # Maximum number of retries


@dataclass
class EmailConfig:
    email_sender: str = 'kamilholb@gmail.com'
    email_receiver: str = 'kamilholb@gmail.com'
    email_password: str = os.getenv('APP_PASSWORD')
    email_subject: str = 'PlantMarketplace Email Test'
    email_body: str = """I've test my email appi"""


@dataclass
class GoogleConfig:
    default_sender:str = 'kamilholb@gmail.com'
    smtp_server:str = 'smtp.gmail.com'
    smtp_port:int = 465
    smtp_username:str = 'kamilholb@gmail.com'
    smtp_password:str = 'iwyj juvk dees ctcx'