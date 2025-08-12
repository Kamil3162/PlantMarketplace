from typing import Optional, Dict, Any


class BaseServiceException(Exception):
    """
        Bazowa klasa dla wszystkich wyjątków serwisów
    """
    def __init__(
        self,
        status_code: int,
        detail: str,
        service_name: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.service_name = service_name
        self.headers = headers


class ServiceNotFoundException(BaseServiceException):
    """
        Gdy nie znajdziemy zasobu w serwisie Django
    """
    def __init__(self, service_name: str, details: str = None):
        super().__init__(
            status_code=404,
            detail=f"Details not found in {service_name} service",
            service_name=service_name
        )


class ServiceUnavailableException(BaseServiceException):
    """
        Gdy serwis Django nie odpowiada
    """
    def __init__(self, service_name: str, details: str = None):
        super().__init__(
            status_code=503,
            detail=f"Service {service_name} is not aviable",
            service_name=service_name
        )


class ServiceTimeoutException(BaseServiceException):
    """
        Gdy serwis Django za długo odpowiada
    """
    def __init__(self, service_name: str, details: float = None):
        super().__init__(
            status_code=504,
            detail=f"Service {service_name} timeout after {details}s",
            service_name=service_name
        )

class ServiceConnectionRefusedException:
    def __init__(self, service_name: str, details: float = None):
        super().__init__(
            status_code=502,
            detail=f"Service {service_name} timeout after {details}s",
            service_name=service_name
        )


class ServiceDNSException(BaseServiceException):
    def __init__(self, service_name: str, details: str = "unknown"):
        super().__init__(
            status_code=502,
            detail=f"DNS resolution failed for {details}",
            service_name=service_name
        )


class ServiceForbiddenException(BaseServiceException):
    def __init__(self, service_name: str, details:str = None):
        super().__init__(
            status_code=403,
            detail=f"You have not access to: {service_name} {details}",
            service_name=service_name
        )

class ServiceMethodException(BaseServiceException):
    def __init__(self, service_name: str, method: str = None):
        super().__init__(
            status_code=403,
            detail=f"Service doesn't have request with method: {method.upper()}",
            service_name=service_name
        )


class ServiceLoopException(BaseServiceException):
    def __init__(self, service_name:str, details: str = None):
        super().__init__(
            status_code=508,
            detail="Detected infinite loop",
            service_name=service_name
        )


class ServiceDataTypeException(BaseServiceException):
    """
        Gdy opowiedz nie jest w typie do parsowania przez JSON
    """
    def __init__(self, service_name: str, details: str = None):
        super().__init__(
            status_code=400,
            detail=f"Bad data type, expected str or bytes, passed variable is {details}",
            service_name=service_name
        )

class ServiceGatewayTimeOutException(BaseServiceException):
    """
        Gdy serwer w tym momencie nie jest w stanie wyslac resposne
        bo sie laduje albo cos
    """

    def __init__(self, service_name: str, details: str = None):
        super().__init__(
            status_code=504,
            detail=f"Gateway Timeout Exception",
            service_name=service_name
        )


class ServiceGatewayException(BaseServiceException):
    def __init__(self, service_name: str, details: str = None):
        super().__init__(
            status_code=502,
            detail=f"{service_name} bad gateway",
            service_name=service_name
        )


class ServiceTooManyRequestsException(BaseServiceException):
    def __init__(self, service_name: str, details: str = None):
        super().__init__(
            status_code=429,
            detail=f"Sent too many requests",
            service_name=service_name
        )


class ServiceNotImplementedException(BaseServiceException):
    def __init__(self, service_name: str, details: str = None):
        super().__init__(
            status_code=501,
            detail=f"{details} Not Implemented",
            service_name=service_name
        )

class ServiceInternalErrorException(BaseServiceException):
    """Serwis się wywalił"""
    def __init__(self, service_name: str, details: str = None):
        super().__init__(
            status_code=500,
            service_name=service_name,
            detail=f"Internal server error: {details}"
        )
        self.is_retriable = True


class TokenNotFound(BaseServiceException):
    """
        Gdy mechanism nie istnieje w headerze requesta
    """
    def __init__(self, service_name: str = "authenticate", details: str = None):
        super().__init__(
            status_code=401,
            detail=details,
            service_name=service_name
        )


class ServiceConnectionTimeoutException(BaseServiceException):
    """Connection timeout"""
    def __init__(self, service_name: str, details: str = None):
        super().__init__(
            status_code=502,
            detail=f"Connection timeout to {service_name}",
            service_name=service_name
        )

class ServiceReadTimeoutException(BaseServiceException):
    """Read timeout"""
    def __init__(self, service_name: str, details: float = None):
        super().__init__(
            status_code=504,
            detail=f"Read timeout after {details}s",
            service_name=service_name
        )

class ServiceUnauthorizedException(BaseServiceException):
    """401 Unauthorized"""
    def __init__(self, service_name: str, details: str = None):
        super().__init__(
            status_code=401,
            detail="Authentication failed",
            service_name=service_name
        )
