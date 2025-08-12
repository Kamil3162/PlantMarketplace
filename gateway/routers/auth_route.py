import json
from typing import Optional

from pydantic import BaseModel, ValidationError
from fastapi import APIRouter, Request, Path
from fastapi.responses import JSONResponse

from microservices_provider import AuthClient

router = APIRouter(
    prefix="/authenticate",
)

auth_client = AuthClient()

@router.api_route("/api/v1/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def auth_proxy(request: Request, path:str):
    request_method = request.method

    if request.method == "POST":
        data_json = await request.json()
    else:
        data_json = None

    response = await auth_client.make_request(
        endpoint=path,
        method=request_method,
        json_data=data_json
    )

    return response

@router.api_route("/authenticate/render-csrf/", methods=["GET"])
async def csrf_token_generate(request: Request):

    path = "/authenticate/render-csrf/"
    response = await auth_client.make_request(path)

    return response


