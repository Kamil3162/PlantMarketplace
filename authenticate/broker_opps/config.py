from dataclasses import dataclass


@dataclass
class RedisConfig:
    pass

@dataclass
class CeleryConfig:
    name: str = "GatewayQueue"


@dataclass
class RabbitMQConfig:
    exachage_name: str = 'auth'
    queue_name : str = 'auth_queue'
    routing_key: str = 'auth'
    host: str = 'gateway-gateway-rabbitmq-1' # here we have to get value from global instance rabbitmq uisng network
    micro_host: str = 'gateway-rabbitmq'
    port: int = 5672
    username: str = 'gateway_user'
    password: str = 'gateway_pass'
    extenstion: str = 'json'

