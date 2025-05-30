import datetime

import jwt
import uuid

from fastapi import Cookie, FastAPI, Query, Header
from core.config import SECRET_KEY

class AuthService:
    ALGORITHM = 'HS256'
    DEFAULT_EXPIRY_SECONDS = 3600
    SECRET_KEY = SECRET_KEY

    @classmethod
    def decode_token(cls, token):
        """
            Decodes and validates a JWT token.

            Args:
                secret_key:
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
                SECRET_KEY,
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token")

    @classmethod
    def encode_token(cls, user_id: uuid) -> dict:
        """
            Encodes user data to JWT token

            Args:
                secret_key:
                user_id: int
                expires_delta - timedelta - timedelta

            Returns:
                Dictionary access_token
        """
        now = datetime.now(timezone.utc)
        expire_time = now + timedelta(seconds=cls.DEFAULT_EXPIRY_SECONDS)

        payload = {
            "token_type": "access",
            "exp": int(expire_time.timestamp()),
            "iat": int(now.timestamp()),
            "jti": str(uuid.uuid4().hex),  # Unique token identifier
            "user_id": user_id
        }

        access_token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=cls.ALGORITHM,
        )

        return access_token

    @classmethod
    def is_token_valid(cls, token: str) -> bool:
        try:
            pay_load = cls.decode_token(token)

            # Compare expiration timestamp with current time
            current_time = datetime.now(timezone.utc).timestamp()
            exp_token = pay_load.get('exp', None)

            # Check if expiration time exists
            if exp_token is None:
                return False

            if current_time > exp_token:
                return False

            return True

        except Exception as e:
            # Handle potential decode errors or invalid tokens
            return False

