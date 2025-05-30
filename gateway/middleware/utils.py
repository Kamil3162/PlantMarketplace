from functools import wraps
from typing import Optional

from fastapi import Request, Response

from exceptions import InvalidRequestError
def validate_user_token(redirect_url='', api_response=False):
    def decorator(view_function):
        @wraps(view_function)
        def wrapper(request, *args, **kwargs):
            user_token = get_request_token(request)
            return view_function(request, *args, **kwargs)
        return wrapper
    return decorator()


def get_request_token(request):
    try:
        if request is None:
            raise InvalidRequestError("Request object cannot be None")

        if not hasattr(request, 'COOKIES'):
            raise InvalidRequestError("Request object has no COOKIES attribute")

        token = request.COOKIES.get('access_token', None)

        if token is None:
            raise TokenNotFoundError("Access token not found in request cookies")

        if is_token_expired(token):  # You would need to implement this function
            raise ExpiredTokenError("The access token has expired")

        return token

    except Exception as e:
        raise  # Re-raise the exception


