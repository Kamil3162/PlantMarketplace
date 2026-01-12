from typing import Any
from dataclasses import dataclass
import consul
from typing import Optional
from enum import Enum

from functools import cache, lru_cache

@dataclass
class ConsulConfig:
    host: str = "127.0.0.1"
    port: int = 8500
    token: str = None
    scheme: str = None
    consistency: str = None
    verify: bool = False
    cert: Any = None

class ServiceStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CRITICAL = "critical"
    OTHER = "other"

def create_url(address: str, port: int) -> str:
    return f"http://{address}:{port}"

class ConsulConnect:

    SERVICE_TYPES = ['account', 'user', 'api', 'payment', 'order']

    def __init__(self, config: ConsulConfig):
        self.consul = consul.Consul(
            config.host,
            config.port,
            verify=config.verify,
            cert=config.cert,
        )
        self.services = {}

    def list_services(self):
        response = self.consul.agent.services()

        for service_type in self.SERVICE_TYPES:
            self.services[service_type] = {}

            for service_id, service_data in response.items():
                if service_id.startswith(service_type):
                    self.services[service_type][service_data['ID']] = {
                        'id': service_id,
                        'address': service_data['ID'],
                        'port': service_data['Port'],
                        'url': f"http://{service_data['ID']}:{service_data['Port']}"
                    }

    def check_service_status(self, service_type: str, service_name: str, status: str) -> str:
        if status not in ServiceStatus:
            raise ValueError(f"Invalid service status: {status}")
        try:
            group_service = self.services[service_type]
            service_info = group_service[service_name]
            return service_info['status']
        except KeyError as e:
            print(f"Error: {e}")
            return None

    def assign_services_statues(self) -> None:
        services_info = self.consul.agent.checks()
        for key, service_info in services_info.items():
            try:

                _, service_name = key.split(':')
                service_group = service_name.split("-")[0]

                _, main_service_name = service_info['CheckID'].split(":")
                service_status = service_info.get('Status', 'Error')

                self.services[service_group][main_service_name][
                    'status'] = service_status
            except (ValueError, KeyError, IndexError) as e:
                print(f"Error during parse services info: {e}")
                continue

    def get_service_url(self, service_type: str) -> Optional[str | None]:
        import random
        if service_type in self.services and self.services[service_type]:
            healthy_services = list(filter(
                lambda service_id: self.services[service_type][service_id][
                                       'status'] == 'passing',
                self.services[service_type]
            ))

            if healthy_services:
                rand_service = random.choice(healthy_services)
                return self.services[service_type][rand_service].get('url', None)
        return None

    @property
    def services_types(self) -> list:
        return self.SERVICE_TYPES

    def get_services_name_by_type(self, service_type: str) -> set:
        if service_type not in self.services_types:
            raise ValueError(f"Service type {service_type} is not defined")

        return set(self.services[service_type].keys())


consul_conf = ConsulConnect(ConsulConfig())
consul_conf.list_services()

print(consul_conf.__dict__)
print(consul_conf.services_types)
print(consul_conf.get_services_name_by_type('api'))

# print(consul_conf.check_service_status('api', ''))
# print(consul_conf.services)
# print(consul_conf.get_service_url('api'))

