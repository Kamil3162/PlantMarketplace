import enum

class ServiceName(enum.Enum):
    USER_SERVICE = "user_service"
    PRODUCT_SERVICE = "product_service"
    AUTH_SERVICE = "auth_service"
    EMAIL_SERVICE = "email_service"


class SericeURLS(enum.Enum):
    USER_SERVICE = "http://user-service:8000"
    PRODUCT_SERVICE = "http://product-service:8000"
    AUTH_SERVICE = "http://auth-service:8000"
    EMAIL_SERVICE = "http://email-service:8000"



