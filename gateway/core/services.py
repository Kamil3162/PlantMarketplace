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
    ServiceName.USER_SERVICE.value: SericeURLS.USER_SERVICE,
    ServiceName.PRODUCT_SERVICE.value: SericeURLS.PRODUCT_SERVICE,
    ServiceName.AUTH_SERVICE.value: SericeURLS.AUTH_SERVICE,
    ServiceName.EMAIL_SERVICE.value: SericeURLS.EMAIL_SERVICE,
}


class ServiceConfig(enum.Enum):
    AUTH_SERVICE = {
        "name": "auth",
        "url": "http://auth-service:8000",
        "path_prefix": "/auth",
        "no_auth_paths": ["login", "register", "forgot-password",
                          "verify-email"]
    }

    USER_SERVICE = {
        "name": "user",
        "url": "http://user-service:8000",
        "path_prefix": "/users",
        "no_auth_paths": []  # GET /users/public-profile/123
    }

    PRODUCT_SERVICE = {
        "name": "product",
        "url": "http://product-service:8000",
        "path_prefix": "/products",
        "no_auth_paths": ["search", "list", "details", "categories"]
        # publiczny katalog
    }

    ORDER_SERVICE = {
        "name": "order",
        "url": "http://order-service:8000",
        "path_prefix": "/orders",
        "no_auth_paths": []  # wszystko wymaga auth
    }

    EMAIL_SERVICE = {
        "name": "email",
        "url": "http://email-service:8000",
        "path_prefix": "/emails",
        "no_auth_paths": []  # wszystko wymaga auth
    }
