import os
from django.apps import AppConfig
import socket
import requests


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data'

    def ready(self):
        try:
            import consul
            consul_host = os.getenv('CONSUL_HOST')
            consul_port = os.getenv('CONSUL_PORT')

            c = consul.Consul(
                host=consul_host,
                port=consul_port,
            )

            hostname = socket.gethostname()
            container_ip = socket.gethostbyname(hostname)

            service_name = os.getenv('SERVICE_NAME', 'product-service')
            service_port = os.getenv('SERVICE_PORT', '8000')
            service_id = f'{service_name}:{service_port}'

            if isinstance(service_port, str):
                service_port = int(service_port)

            print(f'Service port: {service_port}')

            c.agent.service.register(
                name=service_name,
                port=service_port,
                service_id=service_id,
                tags=['django', 'products'],
                check=consul.Check.http(
                    f'http://{container_ip}:{service_port}/health/',
                    interval='10s'
                )
            )

        except ModuleNotFoundError:
            raise
        except ImportError:
            raise
        except Exception as e:
            print(e)

