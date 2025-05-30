from datetime import datetime, timedelta, timezone
import uuid
import jwt

from core.config import SECRET_KEY

class JWTManager(object):
    ALGORITHM = 'HS256'
    DEFAULT_EXPIRY_SECONDS = 3600

    @classmethod
    def create_access_token(cls, user_id: int):
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

    @staticmethod
    def decode_token(token: str) -> dict:
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

