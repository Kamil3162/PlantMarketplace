from datetime import datetime, timedelta
from dataclasses import dataclass

import jwt
from django.conf import settings

from .models import AccessToken
from account.scheme import UserScheme

class JWTManager(object):
    def __init__(self):
        pass

    @staticmethod
    def create_access_token(data: dict, expires_delta=None):
        """
            Encodes user data to JWT token

            Args:
                data: dict - django User model in dict format
                expires_delta - timedelta - timedelta

            Returns:
                Dictionary access_token
        """
        payload = data.copy()
        expire = datetime.utcnow() + timedelta(seconds=900)
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)

        payload.update({
            'exp': expire,
            'iat': datetime.utcnow(),   # creation token time
        })

        access_token = jwt.encode(
            data,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        return access_token

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decodes and validates a JWT token.

        Args:
            token: The JWT token string to decode

        Returns:
            Dictionary containing the decoded payload

        Raises:
            jwt.ExpiredSignatureError: If token has expired
            jwt.InvalidTokenError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token")

