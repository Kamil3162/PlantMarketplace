from functools import wraps

from .redis_manager import RedisManager
from .jwt_manager import JWTManager
from .exceptions import (
    UnauthorizedAccess,
    MissingTokenError,
    BaseError,
    InvalidTokenError
)
from django.forms.models import model_to_dict

from account.utils import get_user
from permissions.models import PermissionGroupAssigment
from account.exceptions import UserNotFound
from .exceptions import PermissionDenied


redis_instance = RedisManager()

def get_token_from_request(request):
    return request.COOKIES.get('access_token', False)

def black_token_validation(func):
    """
        Function use to validate does token exists in blacklisted tokens.
        We wanna prevent to reuse one more time during steal token unautorized acceess
    Args:ssss
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

            user_data = JWTManager.decode_token(access_token)
            request.user_id = user_data['user_id']
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


def check_access_token(required_group=None):
    """
        Function use to user valid token exists in user-tokens, during each operation
    Returns:
    """
    def decorator(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            try:
                access_token = get_token_from_request(request)

                if not access_token:
                    raise MissingTokenError('No access token provided')

                decoded_token = JWTManager.decode_token(access_token)
                user_id = decoded_token['user_id']

                if not user_id:
                    raise InvalidTokenError('Token missing user_id claim')

                user = get_user(user_id)
                user_data = user
                if user is None:
                    raise UserNotFound('Following user does not exists exists')

                if required_group:
                    has_permissions = (
                        PermissionGroupAssigment.objects.
                        check_group_permission(user, required_group)
                    )

                    if not has_permissions:
                        raise PermissionDenied('User has no permissions')

            except InvalidTokenError as e:
                raise InvalidTokenError(str(e))
            except UserNotFound as e:
                raise UserNotFound(str(e))
            except Exception as e:
                raise BaseError(str(e))
            return function(request, user_data=user_data, *args, **kwargs)
        return wrapper
    return decorator

def admin_access_required(function):
    """
    Combined decorator that validates token and checks admin status.
    Args:
        function:
    Returns:
    """
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        try:
            access_token = get_token_from_request(request)
            if not access_token:
                raise MissingTokenError('No access token provided')

            user_data = JWTManager.decode_token(access_token)
            user_id = user_data['user_id']
            # user not found will be caught by default django work flow
            user = get_user(user_id)

            if not user.is_staff:
                raise UnauthorizedAccess(
                    'Access denied. Insufficient permissions'
                )

            return function(request, *args, **kwargs)
        except MissingTokenError as e:
            raise MissingTokenError(str(e))
        except UnauthorizedAccess as e:
            raise UnauthorizedAccess(str(e))
        except Exception as e:
            raise BaseError(str(e))
    return wrapper
