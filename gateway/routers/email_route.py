from fastapi import APIRouter, Request, Header, Depends, Cookie, status
from services.http_client import email_client
from core.exceptions import ServiceNotFoundException, ServiceUnavailableException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyCookie
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/email", tags=["email"])
security = HTTPBearer()

@router.get("/users/{user_id}/emails")
async def get_user_emails(user_id: int):
    """
    Pobierz emaile użytkownika
    """
    try:
        print(user_id)

        emails = await email_client.call_email_service(
            path="/email/base"
        )
        return emails

    except ServiceNotFoundException:
        # To automatycznie zwróci 404 do klienta
        raise
    except ServiceUnavailableException:
        # To automatycznie zwróci 503 do klienta
        raise

@router.get('/user')
async def auth_v1(authorization: HTTPAuthorizationCredentials = Depends(security)):

    token = authorization.credentials
    name = authorization.scheme


    return JSONResponse(
        content={
            'mechanism': token,
            'name': name
        },
        status_code=status.HTTP_200_OK
    )

@router.get('/debug/{id}')
async def debug_request(request: Request, id: int):
    print(dict(request))
    # return JSONResponse(
    #     dict(request)
    # )

