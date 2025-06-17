from typing import Dict
import enum

class ServiceName(enum.Enum):
    USER_SERVICE = "users"
    PRODUCT_SERVICE = "product"
    AUTH_SERVICE = "auth"
    EMAIL_SERVICE = "email"

    @classmethod
    def get_service_names(cls):
        return [service.value for service in cls]


class SericeURLS(enum.Enum):
    USER_SERVICE = "http://user-service:8001"
    PRODUCT_SERVICE = "http://product-service:8000"
    AUTH_SERVICE = "http://auth-service:8000"
    EMAIL_SERVICE = "http://email-service:8000"

class NotAuthUrl(enum.Enum):
    LOGIN = "login"
    REGISTER = "register"
    DOCS = "docs"
    API = "/openapi.json"

SERVICES_NAMES = ServiceName.get_service_names()

SERVICE_URLS:Dict[str, str] = {
    ServiceName.USER_SERVICE.value: SericeURLS.USER_SERVICE.value,
    ServiceName.PRODUCT_SERVICE.value: SericeURLS.PRODUCT_SERVICE.value,
    ServiceName.AUTH_SERVICE.value: SericeURLS.AUTH_SERVICE.value,
    ServiceName.EMAIL_SERVICE.value: SericeURLS.EMAIL_SERVICE.value,
}

