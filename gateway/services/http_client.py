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
        email_url = SericeURLS.EMAIL_SERVICE.value  # usuń slash na końcu
        final_url = f"{email_url}{path}/"


        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method='get',
                    url=final_url
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


# Singleton instance
email_client = ServiceClient()