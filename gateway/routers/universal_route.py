from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import Response
import httpx

from core.services import SERVICE_URLS, SERVICES_NAMES
from core.exceptions import (
    BaseServiceException,
    ServiceTimeoutException,
    ServiceUnavailableException,
    ServiceNotFoundException
)

router = APIRouter()

@router.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def universal_proxy(service: str, path: str, request: Request):

    if service not in SERVICES_NAMES:
        raise ServiceUnavailableException(
            service=service,
            resource=path,
        )

    service_url = SERVICE_URLS[service].value
    target_url = f'{service_url}/{path}'
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers= {k: v
                    for k, v in request.headers.items()
                    if k.lower() not in ['host', 'content-length']
                },
                content=await request.body(),
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={
                    k: v for k, v in response.headers.items()
                    if
                    k.lower() not in ['content-encoding', 'transfer-encoding']
                }
            )
        except Exception as e:
            raise e