import httpx
import json


class ErrorFactory:
    """Factory for mapping errors to your custom exceptions"""

    @staticmethod
    def from_httpx_error(error: Exception, service_name: str):
        """Map httpx errors to your custom exceptions"""

        if isinstance(error, httpx.ConnectTimeout):
            return ServiceConnectionTimeoutException(service_name)

        elif isinstance(error, httpx.ReadTimeout):
            return ServiceReadTimeoutException(service_name, 30.0)

        elif isinstance(error, httpx.ConnectError):
            error_msg = str(error).lower()
            if "connection refused" in error_msg:
                return ServiceConnectionRefusedException(service_name)
            elif "name resolution failed" in error_msg or "dns" in error_msg:
                return ServiceDNSException(service_name, "unknown")
            else:
                return ServiceConnectionRefusedException(service_name)

        elif isinstance(error, httpx.TimeoutError):
            return ServiceTimeoutException(service_name, 30.0)

        elif isinstance(error, json.JSONDecodeError):
            return ServiceDataTypeException(service_name, error)

        elif isinstance(error, httpx.HTTPError):
            return ServiceUnavailableException(service_name, str(error))

        else:
            return ServiceInternalErrorException(service_name, str(error))

    @staticmethod
    def from_status_code(status_code: int, service_name: str, response_text: str = ""):
        """Map HTTP status codes to your custom exceptions"""

        status_map = {
            401:ServiceUnauthorizedException,
            403:ServiceForbiddenException,
            404:ServiceNotFoundException,
            500:ServiceTooManyRequestsException,
            501:ServiceInternalErrorException,
            502:ServiceNotImplementedException,
            503:ServiceGatewayException,
            504:ServiceGatewayTimeOutException,
            508:ServiceLoopException
        }

        exception_class = status_map.get(status_code, False)

        if not exception_class:
            return

        return exception_class(service_name=service_name, detail=response_text)

    @staticmethod
    def from_generic_error(error: Exception, service_name: str):
        """Handle any other unexpected errors"""
        return ServiceInternalErrorException(service_name, f"Unexpected error: {str(error)}")