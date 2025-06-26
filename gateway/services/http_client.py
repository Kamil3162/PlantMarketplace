import httpx
from typing import Optional, Dict, Any
from core.exceptions import (
    ServiceNotFoundException,
    ServiceUnavailableException,
    ServiceTimeoutException
)
from core.services import SericeURLS, ServiceName


class ServiceClient:
    def __init__(self):
        self.timeout = 5.0  # 5 sekund wystarczy

    async def call_email_service(
        self,
        path: str,
        method: str = "GET",
        json_data: Optional[Dict[str, Any]] = None
    ):
        """
            Wywołuje Django Email Service
        """

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if json_data and method in ["POST", "PUT", "PATCH"]:
                    response = await client.request(
                        method=method,
                        url=path,
                        data=json_data  # <-- ZMIANA: data zamiast json
                    )
                else:
                    response = await client.request(
                        method=method,
                        url=path,
                    )
                if response.status_code == 404:
                    raise ServiceNotFoundException(
                        service_name="email-service",
                        resource=path
                    )
                elif response.status_code == 500:
                    raise ServiceUnavailableException(
                        service_name="email-service",
                        original_error="Internal server error"
                    )
                elif response.status_code >= 400:
                    raise ServiceUnavailableException(
                        service_name="email-service",
                        original_error=f"HTTP {response.status_code}: {response.text}"
                    )
                print(response)
                print(response.json())
                # Sukces - zwracamy dane
                return response.json()

            except httpx.TimeoutException as e:
                print(str(e))

                raise ServiceTimeoutException(
                    service_name="email-service",
                    timeout=self.timeout
                )
            except httpx.ConnectError as e:
                print(str(e))
                raise ServiceUnavailableException(
                    service_name="email-service",
                    original_error=f"Connection failed: {str(e)}"
                )
            except (ServiceNotFoundException, ServiceUnavailableException, ServiceTimeoutException) as e:
                print(str(e))
                raise
            except Exception as e:
                print(str(e))
                raise ServiceUnavailableException(
                    service_name="email-service",
                    original_error=f"Unexpected error: {str(e)}"
                )

email_client = ServiceClient()