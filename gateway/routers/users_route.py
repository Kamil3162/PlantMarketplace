from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import httpx

from core.services import SericeURLS
from services.http_client import email_client

router = APIRouter(
    prefix="/users",
)
prefix = "/users"
@router.api_route("/{path:path}",
                  methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def user_proxy(path: str, request: Request):
    service_url = SericeURLS.USER_SERVICE.value
    target_url = f"{service_url}{prefix}/{path}"
    method = request.method

    # Pobierz dane z requestu ZAWSZE jako dict
    data = {}
    if method in ["POST", "PUT", "PATCH"]:
        try:
            # Spróbuj JSON
            json_data = await request.json()
            data = json_data if isinstance(json_data, dict) else {}
        except:
            try:
                # Jeśli nie JSON, to form data
                form = await request.form()
                data = dict(form)
            except:
                data = {}

    # Dodaj query params
    if request.url.query:
        target_url += f"?{request.url.query}"

    response = await email_client.call_email_service(
        target_url,
        method=method,
        json_data=data,  # Zawsze dict, nawet pusty {}
    )
    return response







