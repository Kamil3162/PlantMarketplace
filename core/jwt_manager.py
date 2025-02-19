from datetime import timedelta
from dataclasses import dataclass
import jwt

from .models import AccessToken
from account.scheme import UserScheme



class JWTManager(object):
    def __init__(self):
        pass

    @staticmethod
    def create_access_token(self, data: dict, expires_delta: timedelta):
        access_token = jwt.encode(
            payload=data,

        )
    @staticmethod
    def create_refresh_token(self):...

    @staticmethod
    def decode_access_token(self):...

    @staticmethod
    def generate_access_token(self, expires_in=3600):...