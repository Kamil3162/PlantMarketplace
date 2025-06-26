import httpx
from typing import Optional, Dict, Any
from .exceptions import (
    ServiceNotFoundException,
    ServiceUnavailableException,
    ServiceTimeoutException
)
from httpx import Response
from .services import SERVICE_URLS, ServiceName
import json

class BaseServiceClient:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.base_url = SERVICE_URLS.get(service_name)
        self.timeout = 5.0

    async def make_request(
            self,
            endpoint: str,
            method: str = "GET",
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None
    ):
        full_url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=full_url,
                    json=json_data,
                    headers=headers
                )
                if response.status_code == 404:
                    raise ServiceNotFoundException(
                        service_name=self.service_name,
                        resource=endpoint
                    )
                elif response.status_code == 500:
                    raise ServiceUnavailableException(
                        service_name=self.service_name,
                        original_error="Internal server error"
                    )
                elif response.status_code >= 400:
                    print(response.status_code)
                    print(response.headers)
                    print("test wyjebane w to gówno pierdolone")
                    raise ServiceUnavailableException(
                        service_name=self.service_name,
                        original_error=response.json(),
                        status_code=response.status_code
                    )

                if "csrf" in endpoint:
                    print('csrf')
                    response_data = response.json()
                    print(response_data)
                    if isinstance(response_data, dict):
                        d1 = [response_data]
                        return [response_data]

                response_json = response.json()
                return response_json

            except httpx.TimeoutException as e:
                raise ServiceTimeoutException(
                    service_name=self.service_name,
                    timeout=self.timeout
                )
            except httpx.ConnectError as e:
                raise ServiceUnavailableException(
                    service_name=self.service_name,
                    original_error=f"Connection failed: {str(e)}"
                )
            except (ServiceNotFoundException, ServiceUnavailableException,
                    ServiceTimeoutException):
                raise
            except Exception as e:
                raise ServiceUnavailableException(
                    service_name=self.service_name,
                    original_error=f"Unexpected error: {str(e)}"
                )


class EmailClient(BaseServiceClient):
    def __init__(self):
        super().__init__(ServiceName.EMAIL_SERVICE.value)


class UserClient(BaseServiceClient):
    def __init__(self):
        super().__init__(ServiceName.USER_SERVICE.value)


class AuthClient(BaseServiceClient):
    def __init__(self):
        super().__init__(ServiceName.AUTH_SERVICE.value)


class ProductClient(BaseServiceClient):
    def __init__(self):
        super().__init__(ServiceName.PRODUCT_SERVICE.value)  # Pass the service name
