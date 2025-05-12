import os
from dataclasses import dataclass
import dotenv

dotenv.load_dotenv()

@dataclass
class ConfigCelery:
    name: str = 'product-test'
    broker_user: str = os.getenv('RABBITMQ_DEFAULT_USER', 'myuser')
    broker_password: str = os.getenv('RABBITMQ_DEFAULT_PASS', 'mypassword')
    broker_port: int = os.getenv('RABBITMQ_PORT', '5672')
    broker: str = f'pyamqp://{broker_user}:{broker_password}@localhost/{broker_port}'
    redis_broker: str = 'redis://localhost:6379'
    result_backend: str = 'localhost:8001'
    accept_content: str = 'json'
    task_serializer: str = 'json'
    result_serializer: str = 'json'
    timezone: str = 'Europe/Warsaw'
    enable_utc: bool = True


@dataclass
class EmailConfig:
    email_sender: str = 'kamilholb@gmail.com'
    email_receiver: str = 'kamilholb@gmail.com'
    email_password: str = os.getenv('APP_PASSWORD')
    email_subject: str = 'PlantMarketplace Email Test'
    email_body: str = """I've test my email appi"""