from httpx import Limits, Timeout, AsyncClient
import json
import asyncio
from contextlib import asynccontextmanager
import httpx
from typing import Optional, Dict, Any
from .exceptions import (
    ServiceNotFoundException,
    ServiceUnavailableException,
    ServiceTimeoutException,
    ServiceDataTypeException,
    ServiceGatewayTimeOutException
)
from httpx import Response
from .services import SERVICE_URLS, ServiceName


class BaseServiceClient:
    def __init__(self, service_name: str):
        self.service_name = service_name

        if not SERVICE_URLS.get(service_name, None):
            raise ServiceDoesNotExists(f"Service {service_name} does not exists")

        self.base_url = SERVICE_URLS.get(service_name, None)
        self.timeout = 1
        self.retries = 3
        self.current_try = 1
        self.load_client = httpx.AsyncClient()

    async def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        full_url = f"{self.base_url}{endpoint}"

        for attempt in range(self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method,
                        url=full_url,
                        json=json_data,
                        headers=headers
                    )

                    if response.status_code >= 400:
                        raise ErrorFactory.from_status_code(response.status_code, self.service_name)

                    response_content = response.content
                    if response.headers.get('content-type', '').startswith('application/json'):
                        response_content = response.json()

                    return Response(
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        json=response_content
                    )

            except Exception as exc:
                last_exception = exc

                if attempt == self.retries:
                    return Response(
                        status_code=500,
                        content=str(exc)
                    )

                await asyncio.sleep(0.5 ** attempt)

    async def load_services(self):
        # url we pass into our consul instance
        pass


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
        super().__init__(ServiceName.PRODUCT_SERVICE.value)






