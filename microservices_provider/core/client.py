from httpx import Limits, Timeout, AsyncClient
import json
import asyncio
from contextlib import asynccontextmanager

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
from utils.error_factory import ErrorFactory


class BaseServiceClient:
    def __init__(self, service_name: str):
        self.service_name = service_name

        if not SERVICE_URLS.get(service_name, None):
            raise ServiceDoesNotExists(f"Service {service_name} does not exists")

        self.base_url = SERVICE_URLS.get(service_name, None)
        self.timeout = 1
        self.retries = 3
        self.current_try = 1

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
                    break

                await asyncio.sleep(0.5 ** attempt)

        raise ErrorFactory.from_generic_error(last_exception, self.service_name)


class EmailClient(BaseServiceClient):
    _instance: EmailClient = None

    def __init__(self):
        super().__init__(ServiceName.EMAIL_SERVICE.value)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class UserClient(BaseServiceClient):
    def __init__(self):
        super().__init__(ServiceName.USER_SERVICE.value)


class AuthClient(BaseServiceClient):
    def __init__(self):
        super().__init__(ServiceName.AUTH_SERVICE.value)


class ProductClient(BaseServiceClient):
    def __init__(self):
        super().__init__(ServiceName.PRODUCT_SERVICE.value)


class EmailClientPool:
    _connection_pool: list[BaseServiceClient] = []
    _connection_limit: int = 10
    _initialized: bool = False
    _lock:asyncio.Lock = asyncio.Lock()

    def __new__(cls):
        if not cls._initialized:
            cls._initialized = super().__new__(cls)
        return cls._initialized

    def __init__(self, connection_limit: int):
        pass

    def add_connection(self, connection_client: BaseServiceClient):
        if len(self._connection_pool) < 10:
            self._connection_pool.append(connection_client)

class EmailService:
    @staticmethod
    def create_client() -> AsyncClient:
        return AsyncClient(
            timeout=Timeout(10),
            limits=Limits(
                max_keepalive_connections=3,
                keepalive_expiry=5
            )
        )

    @staticmethod
    @asynccontextmanager
    def client():
        client = EmailService.create_client()
        try:
            yield client
        finally:
            client.aclose()


