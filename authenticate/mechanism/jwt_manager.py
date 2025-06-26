from datetime import datetime, timedelta, timezone
import uuid
import jwt

from django.conf import settings


class JWTManager(object):
    ALGORITHM = 'HS256'
    DEFAULT_EXPIRY_SECONDS = 900

    @classmethod
    def create_access_token(cls, user_id: int):
        """
            Encodes user data to JWT mechanism

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
            "jti": str(uuid.uuid4().hex),  # Unique mechanism identifier
            "user_id": user_id
        }

        access_token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=cls.ALGORITHM,
        )

        return access_token

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decodes and validates a JWT mechanism.

        Args:
            secret_key:
            token: The JWT mechanism string to decode

        Returns:
            Dictionary containing the decoded payload

        Raises:
            jwt.ExpiredSignatureError: If mechanism has expired
            jwt.InvalidTokenError: If mechanism is invalid
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
            raise jwt.InvalidTokenError("Invalid mechanism")

