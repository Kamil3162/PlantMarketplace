from functools import wraps

from django.http import HttpRequest

from core.exceptions import MissingTokenError
from mechanism.redis_manager import RedisManager
from mechanism.jwt_manager import JWTManager
from core.exceptions import (
    UnauthorizedAccess,
    MissingTokenError,
    BaseError,
    InvalidTokenError,
    PermissionDenied
)

redis_instance = RedisManager()

def get_token_from_request(request: HttpRequest):
    auth_header = request.headers.get("AUTHORIZATION")
    if not auth_header:
        raise MissingTokenError("Request does have Authorization Header")
    try:
        token_value = auth_header.split(" ")
        token = token_value[1]
        return token
    except IndexError:
        raise MissingTokenError("Token does not exists")

# function to add token into response
# we have to check and try to get a request into user account to check does this user already exists in our database

def black_token_validation(func):
    """
        Function use to validate does mechanism exists in blacklisted tokens.
        We wanna prevent to reuse one more time during steal mechanism unautorized acceess
    Args:ssss
        func:
        mechanism: jwt mechanism
    Returns:
        Reponse: - redirect
        exception - unatorized access
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            access_token = get_token_from_request(request)

            if not access_token:
                raise MissingTokenError('No access mechanism provided')

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
        Function use to user valid mechanism exists in user-tokens
        We wanna prevent to control and improve flow authentication

    Args:
        mechanism: jwt mechanism
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
        Function use to user valid mechanism exists in user-tokens, during each operation
    Returns:
    """
    def decorator(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            try:
                access_token = get_token_from_request(request)

                if not access_token:
                    raise MissingTokenError('No access mechanism provided')

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
    Combined decorator that validates mechanism and checks admin status.
    Args:
        function:
    Returns:
    """
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        try:
            access_token = get_token_from_request(request)
            if not access_token:
                raise MissingTokenError('No access mechanism provided')

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


def create_response_token(type:str, valid:bool):
    response = {
        "type": type,
        "valid": valid
    }
    return response

def create_success_token_response(type:str, valid:bool, user_id:int):
    response = create_response_token(type, valid)
    response["user_id"] = user_id
    return response