from typing import Optional, Dict, Any
from .exceptions import BaseServiceException

# client error
class ClientErrorException(BaseServiceException):
    def __init__(self, detail:str, status_code:int, service_name:str, headers: Optional[Dict[str, Any]] = None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.service_name = service_name
        self.headers = headers







