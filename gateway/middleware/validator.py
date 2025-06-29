from pprint import pp

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.services import NotAuthUrl, ServiceConfig, SERVICE_URLS
from core.exceptions import TokenNotFound, ServiceUnavailableException
from microservices_provider import AuthClient
from dependencies.auth import AuthService


auth_client = AuthClient()
prefix = "/authenticate/token"

class CredentialsMiddleware(BaseHTTPMiddleware):

    __free_token_urls = [
        NotAuthUrl.LOGIN.value,
        NotAuthUrl.REGISTER.value,
        NotAuthUrl.DOCS.value,
        NotAuthUrl.API.value,
        "/health"
    ]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        free_url = self.__is_free_url(path)

        # we get an user ip using request.client or request.client.host
        # real ip equal Header alias "X-Real-IP"
        # X-Forwarded-For
        forwarded_for = request.headers.get("x-forwarded-for")
        real_ip = request.headers.get("x-real-ip")
        forwarded = request.headers.get("x-forwarded")

        print(forwarded_for, real_ip, forwarded)

        if free_url:
            return await call_next(request)

        try:
            service_name = self.__extract_prefix(path)
            service_name_v1 = self.__check_service_name(service_name)
        except ServiceUnavailableException as e:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Service Not Found",
                    "message": str(e)
                }
            )
        try:
            token = self.__extract_token(request)
            token_valid = AuthService.is_token_valid(token)

            if not token_valid:
                return self.__unauthorized_response("Token has expired")
            return await call_next(request)

        except TokenNotFound as e:
            return self.__unauthorized_response(str(e))
        except Exception as e:
            print(str(e))
            return self.__unauthorized_response("Invalid mechanism")


    def __extract_token(self, request: Request):
        token = request.headers.get("Authorization")
        clean_token = token.split(" ")[1]
        if not clean_token:
            raise TokenNotFound("Token doesn't exist")
        return clean_token

    def __is_free_url(self, path):
        return any(element in path for element in self.__free_token_urls)


    def __unauthorized_response(self, message: str):
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized", "message": message}
        )

    def __extract_prefix(self, path: str):
        parts = path.split("/")
        service_name = parts[1]
        print(f"service_name: '{service_name}'")
        return service_name.lower()

    def __check_service_name(self, service_name: str):
        if service_name not in SERVICE_URLS:
            raise ServiceUnavailableException(
                service_name,
                original_error="Service doesnt exist",
            )
        return SERVICE_URLS[service_name]