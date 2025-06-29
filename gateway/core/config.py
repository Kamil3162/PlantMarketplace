import os
from dataclasses import dataclass, field

import dotenv

dotenv.load_dotenv()

SECRET_KEY = "$+#hqc5(f0#y84^!$a!suex3(k@3dlzphefh42ls=(bk)jrctr"

@dataclass
class CeleryConfig:
    name: str = 'gateway-auth-handler'

    # RabbitMQ configuration
    broker_user: str = os.getenv('RABBITMQ_DEFAULT_USER', 'gateway_user')
    broker_password: str = os.getenv('RABBITMQ_DEFAULT_PASS', 'gateway_pass')
    broker_host: str = os.getenv('RABBITMQ_HOST', 'gateway-rabbitmq')  # Use service name in docker
    broker_port: int = os.getenv('RABBITMQ_PORT', '5672')
    broker_url: str = f'amqp://{broker_user}:{broker_password}@{broker_host}:{broker_port}//'

    # Task settings
    task_serializer: str = 'json'
    accept_content: list = field(default_factory=lambda: ['json'])
    result_serializer: str = 'json'
    timezone: str = 'Europe/Warsaw'
    enable_utc: bool = True


