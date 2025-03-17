from core.redis_manager import RedisManager
from django.http import HttpRequest
from django.contrib.auth.backends import BaseBackend

from .jwt_manager import JWTManager
from .redis_manager import RedisManager
from .utils import get_user, get_token_from_request





