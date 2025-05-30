from fastapi import HTTPException
from typing import Optional, Dict, Any

class BaseServiceException(HTTPException):
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
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.service_name = service_name

class ServiceNotFoundException(BaseServiceException):
    """
    Gdy nie znajdziemy zasobu w serwisie Django
    """
    def __init__(self, service_name: str, resource: str):
        super().__init__(
            status_code=404,
            detail=f"{resource} not found in {service_name}",
            service_name=service_name
        )

class ServiceUnavailableException(BaseServiceException):
    """
    Gdy serwis Django nie odpowiada
    """
    def __init__(self, service_name: str, original_error: str):
        super().__init__(
            status_code=503,
            detail=f"Service {service_name} is unavailable: {original_error}",
            service_name=service_name
        )

class ServiceTimeoutException(BaseServiceException):
    """
    Gdy serwis Django za długo odpowiada
    """
    def __init__(self, service_name: str, timeout: float):
        super().__init__(
            status_code=504,
            detail=f"Service {service_name} timeout after {timeout}s",
            service_name=service_name
        )