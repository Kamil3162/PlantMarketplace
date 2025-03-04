from functools import wraps

from .redis_manager import RedisManager
from .jwt_manager import JWTManager
from .exceptions import UnauthorizedAccess, MissingTokenError, BaseError

from account.utils import get_user
from account.exceptions import UserNotFound

redis_instance = RedisManager()

def get_token_from_request(request):
    return request.COOKIES.get('access_token', False)

def black_token_validation(func):
    """
        Function use to validate does token exists in blacklisted tokens.
        We wanna prevent to reuse one more time during steal token unautorized acceess
    Args:
        func:
        token: jwt token
    Returns:
        Reponse: - redirect
        exception - unatorized access
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            access_token = get_token_from_request(request)

            if not access_token:
                raise MissingTokenError('No access token provided')

            if redis_instance.is_blocked(access_token):
                raise UnauthorizedAccess('Token has been revoked')

            user_data = JWTManager.decode(access_token)
            if user_data:
                request.user_data = user_data

            return func(request, *args, **kwargs)
        except Exception as e:
            raise BaseError(str(e))
    return wrapper

def remove_access_token(func):
    """
        Function use to user valid token exists in user-tokens
        We wanna prevent to control and improve flow authentication

    Args:
        token: jwt token
    Returns:
        Reponse: - redirect
        exception - unatorized access
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        access_token = get_token_from_request(request)
        redis_instance.block_token(access_token)
        redis_instance.remove_access_token(access_token)
        redis_instance.get_user_data(access_token)
        redis_instance.get_blocked_token(access_token)
        return func(request, *args, **kwargs)
    return wrapper


def check_access_token(function):
    """
        Function use to user valid token exists in user-tokens, during each operation
    Returns:
    """
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        try:
            access_token = get_token_from_request(request)

            if not access_token:
                raise MissingTokenError('No access token provided')

            user_data = JWTManager.decode_token(access_token)
            user_email = user_data['email']
            user = get_user(user_email)

            if user is None:
                raise UserNotFound('Following user doesnt exists')
        except KeyError:
            raise KeyError('user data doesnt have key email')
        except Exception as e:
            raise BaseError(str(e))
        return function(request, *args, **kwargs)
    return wrapper